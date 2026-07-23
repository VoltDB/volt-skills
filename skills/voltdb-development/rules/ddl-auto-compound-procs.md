# Compound Procedures

> **Category:** Automation & Time-Based Processing | **Impact:** MEDIUM

## Context

A **compound procedure** chains multiple transactional stored procedures together with branching, error handling, and arbitrary Java logic — running on the cluster instead of in a client application. It is the tool for business processes that span *differently partitioned* data without paying the cost of one big multi-partition transaction (which blocks every partition until it finishes).

The primary use case is processing inbound topics and import connectors, where there is no client application to orchestrate multiple calls: the topic invokes one procedure per record, and that one procedure sometimes needs to touch several partitions (e.g., look up a device by device ID, then update an account partitioned on account ID).

**The critical trade-off: compound procedures are NOT transactional.** Each queued procedure succeeds or fails on its own; there is no rollback across them. Never present a compound procedure as an atomic alternative to a multi-partition procedure — if the user needs all-or-nothing semantics across the steps, they need a multi-partition procedure (or a redesign, e.g., co-location so a single-partition procedure covers it — see [ddl-multi-step-transactions.md](ddl-multi-step-transactions.md)).

## Rule

### When to generate one

- Inbound topic / Kafka import where per-record processing needs more than one transaction (lookups in one partition, writes in another).
- Server-side orchestration of a multi-step flow that would otherwise live in client code, when the steps tolerate independent success/failure.

When the steps all share one partition key, use a single-partition Java procedure instead — it is transactional and simpler. When the flow is one statement, use a DDL-defined procedure.

### Structure

Extend `VoltCompoundProcedure`; in `run(...)` declare an ordered list of **stages**. Each stage queues transactional procedure calls; when all complete, the next stage receives their results as a `ClientResponse[]` (in queue order):

```java
package devices;

import org.voltdb.VoltCompoundProcedure;
import org.voltdb.VoltTable;
import org.voltdb.client.ClientResponse;

public class ProcessMessage extends VoltCompoundProcedure {

    private long deviceID, accountID;
    private String message;

    public long run(long id, String messagetext) {   // topic record fields arrive as args
        this.deviceID = id;
        this.message = messagetext;
        newStageList(this::deviceLookup)
            .then(this::accountLookup)
            .then(this::writeResults)
            .then(this::finish)
            .build();
        return 0;
    }

    private void deviceLookup(ClientResponse[] none) {
        queueProcedureCall("DEVICE.select", deviceID);
    }

    private void accountLookup(ClientResponse[] resp) {
        VoltTable device = resp[0].getResults()[0];
        if (device.getRowCount() == 0) {
            abortProcedure("No such device: " + deviceID);
            return;
        }
        device.advanceRow();
        accountID = device.getLong("account");
        queueProcedureCall("ACCOUNT.select", accountID);
    }

    private void writeResults(ClientResponse[] resp) {
        // Two calls queued in ONE stage run in parallel, in no guaranteed order.
        // Sequence-dependent calls must go in separate stages.
        queueProcedureCall("ACCOUNT_LOG.insert", accountID, deviceID, message);
        queueProcedureCall("ExtendedMessage.insert", deviceID, accountID, message);
    }

    private void finish(ClientResponse[] resp) {
        // Non-transactional: check EVERY response — a failed call is not rolled back
        StringBuilder alert = new StringBuilder();
        for (ClientResponse r : resp) {
            if (r.getStatus() != ClientResponse.SUCCESS) {
                alert.append(r.getStatusString()).append('\n');
            }
        }
        if (alert.length() > 0) {
            abortProcedure(alert.toString());
        } else {
            completeProcedure(1L);
        }
    }
}
```

Key mechanics:

- Use class fields to carry state between stages.
- Calls queued within a stage run **asynchronously and in parallel** — order is only guaranteed *between* stages.
- Every compound procedure must end by calling `completeProcedure(value)` or `abortProcedure(message)`; otherwise the caller gets UNEXPECTED_FAILURE.
- Default limit is 10 queued calls per stage (`deployment.compoundproc.callsperstage`).

### Declaring and invoking

```sql
-- after LOAD CLASSES devices.jar;
CREATE COMPOUND PROCEDURE FROM CLASS devices.ProcessMessage;
```

- Compound procedures cannot be partitioned (they call procedures across partitions).
- Invoke by associating with an inbound topic (`deployment.topics.topic[].procedure: ProcessMessage`) or an import connector, or call it like any procedure from a client / sqlcmd `exec`.

### Error handling rules (non-negotiable)

Generated compound procedures must always:

1. Check the status of **every** `ClientResponse` in the following stage — a later failure does not undo an earlier success, so the code must detect partial completion.
2. Avoid writes in early stages whose validity depends on writes in later stages (put dependent writes as late as possible).
3. Handle the "no caller" case when invoked from a topic — `abortProcedure` has no application to report to, so log or write failures somewhere durable if the business flow requires follow-up.

Also note: if the node running the compound procedure crashes mid-flight, completed constituent transactions stay committed and the remaining stages simply never run. The design must tolerate that (idempotent re-delivery from the topic is the usual answer).

### Resource tuning

`deployment.compoundproc.callsperstage` (default 10), `.queuelimit` (default 10,000 queued compound procs), `.threads` (default = cores). Mention these only when the user is sizing a high-throughput topic pipeline.

## References

- *VoltDB Guide to Performance and Customization*: "Using Compound Procedures"
- *Using VoltDB*: CREATE COMPOUND PROCEDURE (CREATE PROCEDURE FROM CLASS reference)
- [ddl-auto-overview.md](ddl-auto-overview.md) — feature-selection table
- [ddl-multi-step-transactions.md](ddl-multi-step-transactions.md) — the transactional alternative when all steps share a partition key

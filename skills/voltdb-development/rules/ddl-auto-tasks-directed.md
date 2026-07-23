# Scheduled Tasks and Directed Procedures

> **Category:** Automation & Time-Based Processing | **Impact:** HIGH

## Context

A **task** (`CREATE TASK`) schedules a stored procedure to run automatically — cleanup, pruning, periodic validation, deadline sweeps. Because the task definition is part of the schema, it starts and stops with the database; no external scheduler or cron job is needed.

A **directed procedure** (`CREATE PROCEDURE ... DIRECTED`) runs a separate, independent transaction on *every* partition. Each instance behaves like a single-partition procedure on its own slice of the data, so the partitions are never blocked all at once the way a multi-partition procedure blocks them. Directed procedures are invoked by tasks (`RUN ON PARTITIONS`) or via the client `callAllPartitionProcedure` method — never by plain `callProcedure`.

Tasks + directed procedures are the correct answer for "periodically find rows meeting a condition and act on them" — the requirement users sometimes try to force onto TTL (see [ddl-auto-overview.md](ddl-auto-overview.md)).

## Rule

### CREATE TASK syntax

```sql
CREATE TASK task-name
    ON SCHEDULE {CRON cron-spec | DELAY interval | EVERY interval}
    PROCEDURE procedure-name [WITH (arg, ...)]
    [ON ERROR {LOG | IGNORE | STOP}]
    [RUN ON {DATABASE | PARTITIONS}]
    [AS USER user-name]
    [ENABLE | DISABLE];
```

- **EVERY** = fixed interval between *starts*; **DELAY** = fixed interval between the *end* of one run and the start of the next; **CRON** = six-field cron spec (seconds first) for wall-clock schedules. Intervals accept `MILLISECONDS`, `SECONDS`, `MINUTES`, `HOURS`, `DAYS`.
- **ON ERROR defaults to STOP** — one failed run disables the task until it is re-enabled or the database restarts. For recurring maintenance, `ON ERROR LOG` is usually what the user wants; call this out when generating a task.
- **RUN ON DATABASE** (default) runs the procedure as a normal (typically multi-partition) transaction. **RUN ON PARTITIONS** requires a directed procedure and runs it independently on every partition.
- `AS USER` is required when security is enabled. Manage tasks afterward with `ALTER TASK name DISABLE/ENABLE` and `DROP TASK`.
- Simple example — nightly stats reset:

```sql
CREATE PROCEDURE ResetDailyStats AS DELETE FROM DailyStats;
CREATE TASK nightly
    ON SCHEDULE CRON 0 0 0 * * *
    PROCEDURE ResetDailyStats
    RUN ON DATABASE;
```

### Directed procedures

Declare with `DIRECTED` instead of `PARTITION ON` — works for both DDL-defined and Java procedures:

```sql
CREATE PROCEDURE PurgeOldSessions DIRECTED AS
    DELETE FROM session
        WHERE last_access < DATEADD(MINUTE, -5, NOW())
        ORDER BY sessionID ASC LIMIT ?;

CREATE TASK batchcleanup
    ON SCHEDULE DELAY 5 SECONDS
    PROCEDURE PurgeOldSessions WITH (500)
    ON ERROR LOG
    RUN ON PARTITIONS;
```

- Each partition's instance is transactional on that partition, but the instances are **not coordinated** — no cross-partition atomicity and no guarantee they run at the same moment. Fine for maintenance sweeps; not for logic that must see a globally consistent snapshot.
- Directed procedures must be deterministic, like any transactional procedure.
- The `ORDER BY ... LIMIT ?` batch-delete pattern above is the canonical use: bounded per-partition batches that never block the whole cluster. On partitioned tables, a DELETE with ORDER BY + LIMIT generally *requires* a partitioned or directed procedure.
- **The ORDER BY must end in a unique key** (the primary key or a unique index, or else cover every column). This is what makes the delete pick the same rows on every partition replica and DR target; ordering by a timestamp alone is rejected at DDL-compile time with "DELETE statement manipulates data in a non-deterministic way" whenever values can tie. `ORDER BY expiry_col, pk_col LIMIT ?` is the standard shape. `NOW` is safe in these procedures — it is assigned once at transaction start and identical across replicas, DR, and command-log replay.
- Because `LIMIT` is an **exact** per-partition cap, this pattern also serves as a hard-capped do-it-yourself TTL when the built-in TTL sweep can't bound its batches — TTL's `BATCH_SIZE` is only a target and cannot split rows sharing one timestamp value (see [ddl-auto-ttl-migrate.md](ddl-auto-ttl-migrate.md)). Sizing note: maximum delete throughput is `batch × partitions × passes/hour`; tune with the `PROCEDUREPROFILE` selector of `@Statistics` (keep AVG/MAX execution time below the task interval) and lower the batch or interval if the sweep competes with the production workload.
- Java form: `CREATE DIRECTED PROCEDURE FROM CLASS pkg.MyProc;` (no PARTITION ON clause).
- Index the column the sweep filters on (`last_access` above) — same reasoning as any hot WHERE clause.

### Worked example: deadline detection (missed heartbeats)

Requirement shape: rows represent in-progress state (a monitored device, an open session, a pending request); if no activity happens within N minutes, the system must *do something* — emit an event, alert, escalate. Here, devices report heartbeats, and a device silent for 5 minutes should produce an offline event on a topic:

```sql
CREATE TABLE device_status (
    device_id BIGINT NOT NULL,
    status VARCHAR(16) DEFAULT 'ONLINE' NOT NULL,   -- ONLINE / OFFLINE / RETIRED
    last_heartbeat TIMESTAMP DEFAULT NOW NOT NULL,
    PRIMARY KEY (device_id)
);
PARTITION TABLE device_status ON COLUMN device_id;
CREATE INDEX device_sweep_idx ON device_status (status, last_heartbeat);

-- Outbound event stream: rows inserted here flow to the configured topic/target
CREATE STREAM offline_events
    PARTITION ON COLUMN device_id
    EXPORT TO TOPIC DeviceOfflineEvents
(
    device_id BIGINT NOT NULL,
    detected_at TIMESTAMP NOT NULL
);
```

The sweep is a directed procedure so each partition scans only its own rows. Marking + event emission need two statements, so it is a multi-statement (or Java) procedure:

```sql
CREATE PROCEDURE SweepOfflineDevices DIRECTED AS BEGIN
    INSERT INTO offline_events (device_id, detected_at)
        SELECT device_id, NOW() FROM device_status
        WHERE status = 'ONLINE' AND last_heartbeat < DATEADD(MINUTE, -5, NOW());
    UPDATE device_status SET status = 'OFFLINE'
        WHERE status = 'ONLINE' AND last_heartbeat < DATEADD(MINUTE, -5, NOW());
END;

CREATE TASK offline_sweep
    ON SCHEDULE DELAY 10 SECONDS
    PROCEDURE SweepOfflineDevices
    ON ERROR LOG
    RUN ON PARTITIONS;
```

Why this beats TTL/MIGRATE-to-topic for the same requirement:

- The device row **stays in VoltDB** with its state — follow-up logic (alerting rules, checking the device profile) can run against it without re-ingesting the event from Kafka.
- Each heartbeat is a normal `UPDATE ... SET last_heartbeat = NOW()`; decommissioning sets `status = 'RETIRED'` (or deletes the row). No fighting a deletion timer.
- Detection and the event emission happen in one transaction per partition — a device that reports in just before the sweep never generates a stale offline event.
- The 5-minute deadline lives in one place (the sweep procedure) and can carry arbitrary business logic, not just a column comparison.

If the per-deadline action is too complex for SQL (per-row branching, calling other procedures), the sweep can instead SELECT the expired rows and the follow-up logic can live in a Java directed procedure — or the task can invoke a compound procedure via a client-visible flow (see [ddl-auto-compound-procs.md](ddl-auto-compound-procs.md)).

### Custom tasks (advanced)

When a fixed schedule or fixed arguments aren't enough, a custom task supplies them from Java. Implement one of three interfaces from `org.voltdb.task.*`, load the class with `LOAD CLASSES`, and reference it in `CREATE TASK`:

| Interface | Customizes | CREATE TASK clause |
|---|---|---|
| `ActionGenerator` | procedure + its arguments | `PROCEDURE FROM CLASS cls WITH (...)` |
| `IntervalGenerator` | interval between runs | `ON SCHEDULE FROM CLASS cls WITH (...)` |
| `ActionScheduler` | both | `FROM CLASS cls WITH (...)` (replaces both clauses) |

Each implementation provides `initialize(TaskHelper, ...)`, a `getFirst...()` method, and a callback that receives the previous run's `ActionResult` and returns the next action/interval — e.g., growing or shrinking a delete batch size to match the workload. `WITH (...)` arguments go to `initialize()`, not the procedure. Custom task classes are **not** stored procedures — they run on a separate scheduler thread and only decide what to run next. Custom tasks may also `RUN ON HOSTS` (one instance per server).

Only reach for a custom task when the user explicitly needs adaptive behavior; a plain `CREATE TASK` covers the common cases.

### Testing

Tasks fire on real time, so integration tests should use short schedules (e.g., `DELAY 1 SECONDS`) and poll for the expected effect with a timeout. Alternatively, test the swept procedure directly: directed procedures can be invoked from a test via `callAllPartitionProcedure`, which returns one VoltTable per partition.

## References

- *Using VoltDB*: "Simplifying Application Development" (tasks, directed procedures); CREATE TASK, CREATE PROCEDURE AS / FROM CLASS reference pages
- *VoltDB Guide to Performance and Customization*: "Creating Custom Tasks"
- [ddl-auto-overview.md](ddl-auto-overview.md) — feature-selection table and the TTL/MIGRATE vs. task-sweep trade-off comparison

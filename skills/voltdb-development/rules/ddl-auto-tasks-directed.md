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

### Worked example: deadline detection (the abandoned-cart pattern)

Requirement shape: rows represent in-progress state (a cart, a pending payment, an open session); if no activity happens within N minutes, the system must *do something* — emit an event, generate an offer, escalate.

```sql
CREATE TABLE cart (
    user_id BIGINT NOT NULL,
    cart_id BIGINT NOT NULL,
    status VARCHAR(16) DEFAULT 'ACTIVE' NOT NULL,   -- ACTIVE / ABANDONED / PURCHASED
    last_updated TIMESTAMP DEFAULT NOW NOT NULL,
    PRIMARY KEY (user_id)
);
PARTITION TABLE cart ON COLUMN user_id;
CREATE INDEX cart_sweep_idx ON cart (status, last_updated);

-- Outbound event stream: rows inserted here flow to the configured topic/target
CREATE STREAM abandoned_events
    PARTITION ON COLUMN user_id
    EXPORT TO TOPIC AbandonedEvents
(
    user_id BIGINT NOT NULL,
    cart_id BIGINT NOT NULL,
    abandoned_at TIMESTAMP NOT NULL
);
```

The sweep is a directed procedure so each partition scans only its own rows. Marking + event emission need two statements, so it is a multi-statement (or Java) procedure:

```sql
CREATE PROCEDURE SweepAbandonedCarts DIRECTED AS BEGIN
    INSERT INTO abandoned_events (user_id, cart_id, abandoned_at)
        SELECT user_id, cart_id, NOW() FROM cart
        WHERE status = 'ACTIVE' AND last_updated < DATEADD(MINUTE, -5, NOW());
    UPDATE cart SET status = 'ABANDONED'
        WHERE status = 'ACTIVE' AND last_updated < DATEADD(MINUTE, -5, NOW());
END;

CREATE TASK abandonment_sweep
    ON SCHEDULE DELAY 10 SECONDS
    PROCEDURE SweepAbandonedCarts
    ON ERROR LOG
    RUN ON PARTITIONS;
```

Why this beats TTL/MIGRATE-to-topic for the same requirement:

- The cart row **stays in VoltDB** with its state — the follow-up logic (match an offer, check the profile) can run against it without re-ingesting the event from Kafka.
- Activity resets are a normal `UPDATE ... SET last_updated = NOW()`; a purchase sets `status = 'PURCHASED'` (or deletes the row). No fighting a deletion timer.
- Detection and the event emission happen in one transaction per partition — no race where a returning user still generates an "abandoned" event.
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
- [ddl-auto-overview.md](ddl-auto-overview.md) — feature-selection table and the TTL-as-event-generator anti-pattern

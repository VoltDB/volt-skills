# TTL Expiration and Data Migration

> **Category:** Automation & Time-Based Processing | **Impact:** HIGH

## Context

`USING TTL` automatically deletes rows once a TIMESTAMP column passes an age threshold. Adding `MIGRATE TO TARGET` (export connector) or `MIGRATE TO TOPIC` (VoltDB topic) turns deletion into archiving: the row is exported first and deleted only after the target acknowledges receipt, so the data always exists in at least one system.

**Purpose check:** TTL/MIGRATE is for retention and archiving — removing rows that no longer need to be in memory. If the requirement is to *act* on rows when a deadline passes, use a scheduled task instead (see [ddl-auto-overview.md](ddl-auto-overview.md) and [ddl-auto-tasks-directed.md](ddl-auto-tasks-directed.md)).

## Rule

### Basic TTL

```sql
CREATE TABLE current_alerts (
    id BIGINT NOT NULL,
    message VARCHAR(128),
    created TIMESTAMP DEFAULT NOW NOT NULL,
    PRIMARY KEY (id)
)
USING TTL 5 MINUTES ON COLUMN created;
PARTITION TABLE current_alerts ON COLUMN id;

-- REQUIRED: without a usable index on the TTL column, no rows are ever
-- deleted (the DDL is accepted and only a warning is logged)
CREATE INDEX alerts_ttl_idx ON current_alerts (created);
```

- The TTL column must be `TIMESTAMP` and `NOT NULL`. Units: `SECONDS` (default), `MINUTES`, `HOURS`, `DAYS`.
- **An index on the TTL column is mandatory in practice.** The clause is accepted without one, but the background sweep does nothing until a usable index exists — a silent failure mode.
- TTL is evaluated against the *current* column value, so updating the column extends (or shortens) the row's life.
- Deletion happens shortly *after* expiry, not at the exact moment — the sweep is a periodic background process, and each deletion is a normal transaction (it shows up in the workload).
- **Prefer TTL on partitioned tables.** On a replicated table every TTL delete is a multi-partition transaction, which can significantly impact throughput.

### TTL requires high cardinality in the TTL column

How the sweep bounds its work: on each pass (per partition — `BATCH_SIZE` applies per partition), if more than `BATCH_SIZE` rows qualify, it looks up the TTL-column *value* at the `BATCH_SIZE`-th qualifying row and uses that as a cutoff, then deletes every row at or below the cutoff value in one transaction. The delete is by **value**, not by row count — `BATCH_SIZE` is a target, not a hard limit, and the sweep cannot split a group of rows that share the same TTL-column value.

Consequences when many rows share one value (e.g., a timestamp truncated to day granularity, or an expiry stamped onto a large set of rows by one bulk operation):

- A single pass deletes *all* rows at that value in one transaction, however many there are — a latency spike at minimum.
- On clusters using DR, an over-sized TTL delete can exceed the 50 MB limit on a single DR binary-log transaction. TTL then **suspends itself on that table** (server warning contains `bytes exceeds max DR Buffer size`) and does not resume until the configuration or data changes and it is re-enabled. The visible symptoms are "TTL ignores BATCH_SIZE" and "TTL stopped working on this table."

**Generation-time check — apply whenever emitting `USING TTL`:** confirm the TTL column will have many distinct values *within each partition*.

- Naturally fine: per-row insert/update timestamps (`DEFAULT NOW` — microsecond precision).
- Needs attention: expiry columns computed at coarse granularity (day/hour), or set in bulk to a shared future value. If the design has this shape, warn the user and either spread the values (e.g., add per-row jitter within the retention window) or use the hard-capped sweep below.

**Hard-capped alternative:** a scheduled task driving a directed procedure with `DELETE ... ORDER BY ... LIMIT ?` deletes an *exact* maximum number of rows per partition per pass, regardless of how timestamps are distributed (see the batch-delete pattern in [ddl-auto-tasks-directed.md](ddl-auto-tasks-directed.md)). It costs one procedure plus one task per table, so don't reach for it by default — plain TTL is less boilerplate and is the right choice whenever the column is naturally high-cardinality.

### TTL + migration (automatic archiving)

```sql
CREATE TABLE sessions
    MIGRATE TO TARGET oldsessions
(
    user_id BIGINT NOT NULL,
    login TIMESTAMP DEFAULT NOW,
    last_update TIMESTAMP NOT NULL,
    PRIMARY KEY (user_id)
)
USING TTL 1 HOURS ON COLUMN last_update;
PARTITION TABLE sessions ON COLUMN user_id;

-- REQUIRED when combining TTL with MIGRATE: a partial index on only the
-- TTL column, filtered on NOT MIGRATING. Without it, rows are neither
-- deleted nor migrated (warning logged on the server).
CREATE INDEX sessions_migrate_idx ON sessions (last_update) WHERE NOT MIGRATING;
```

- `MIGRATE TO TARGET x` sends rows through the export connector configured for target `x` in the deployment configuration; `MIGRATE TO TOPIC x` writes them to a VoltDB topic. Either way the row is deleted only after the target acknowledges it.
- The export target or topic must be configured in the deployment (server-side) configuration — the DDL alone does nothing. In generated testcontainer projects there is normally no export infrastructure, so only propose MIGRATE when the user has (or wants) a target to receive the data.

### Manual migration

`MIGRATE TO TARGET` without `USING TTL` gives you an archiving path with application-controlled selection:

```sql
MIGRATE FROM messages
  WHERE posted < DATEADD(DAY, -3, NOW()) AND NOT MIGRATING;
```

- `AND NOT MIGRATING` is not required (rows already migrating are skipped) but improves performance.
- Manual `MIGRATE` also works alongside `USING TTL` for preemptive archiving (e.g., migrate a user's rows when the account is deleted).

### The MIGRATING window

Between expiry and target acknowledgment, the row is still visible to SELECT and can be updated or deleted:

- An UPDATE during this window **cancels the pending delete but not the already-triggered export** — the original row values still reach the target, and the modified row stays in the table (eventually migrating again). This is why TTL/MIGRATE cannot be used as a reliable "nothing happened before the deadline" event source.
- Guard writes on TTL/MIGRATE tables with `AND NOT MIGRATING` to avoid touching rows already on their way out:

```sql
UPDATE sessions SET last_update = NOW() WHERE user_id = ? AND NOT MIGRATING;
```

### Tuning

`USING TTL ... BATCH_SIZE n MAX_FREQUENCY f` — maximum rows deleted per cycle (default 1000) and maximum sweep cycles per second (default 1). Adjust when TTL falls behind under heavy insert load, or when very wide rows risk exceeding the temporary table limit. The `TTL` selector of the `@Statistics` system procedure reports sweep performance.

### Testing

TTL deletion is asynchronous — an integration test that inserts an expired row must poll for its disappearance (with a timeout) rather than assert immediately. Keep test TTLs short (seconds) so tests stay fast.

## References

- *Using VoltDB*: CREATE TABLE — "Automatic Aging and Data Migration"; MIGRATE statement; MIGRATING function; export chapter ("Using VoltDB as a Hot Cache")
- [ddl-auto-overview.md](ddl-auto-overview.md) — when TTL is and is not the right feature

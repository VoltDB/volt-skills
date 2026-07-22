# Choosing the Right Feature for Time-Based and Event-Driven Work

> **Category:** Automation & Time-Based Processing | **Impact:** HIGH

## Context

VoltDB has several built-in features for work that is driven by time or by data arrival rather than by a client request: TTL (time to live), data migration, scheduled tasks, directed procedures, export streams, and compound procedures. Because these were added over the years on top of the core schema objects, many users know them less well than tables, indexes, and ordinary procedures — and a feature the user already knows can end up pressed into a job another feature was designed for (for example, TTL used as an event generator).

Use this rule to map the user's requirement to the right feature **before** generating DDL. Read the detail rule for whichever feature applies:
- [ddl-auto-ttl-migrate.md](ddl-auto-ttl-migrate.md) — TTL expiration and data migration
- [ddl-auto-tasks-directed.md](ddl-auto-tasks-directed.md) — scheduled tasks and directed procedures
- [ddl-auto-compound-procs.md](ddl-auto-compound-procs.md) — compound procedures

## Rule

Match the requirement to the feature designed for it:

| Requirement | Feature |
|---|---|
| Delete old rows that no longer need to be in memory | `USING TTL` on the table |
| Archive old rows to an external system before deleting them | `MIGRATE TO TARGET` (or `TO TOPIC`) + `USING TTL` |
| Move selected rows out of VoltDB on demand, with complex criteria | `MIGRATE TO TARGET` + explicit `MIGRATE FROM ... WHERE ...` statement |
| Emit a business event to Kafka/an export target from procedure logic | `INSERT INTO` a stream declared with `EXPORT TO TOPIC` / `EXPORT TO TARGET` |
| Run maintenance or business logic on a schedule (cleanup, stats reset, sweeps) | `CREATE TASK` |
| Scheduled per-partition work that must not block the whole cluster (batch deletes, deadline sweeps on partitioned tables) | Directed procedure + `CREATE TASK ... RUN ON PARTITIONS` |
| Detect records that passed a deadline and **act** on them (inactivity timeouts, missed heartbeats, SLA breaches) | Task + directed procedure sweep — **not** TTL |
| Multi-step logic spanning partitions when processing an inbound topic or import | Compound procedure |
| Schedule or batch size that adapts to workload | Custom task (`ActionGenerator` / `IntervalGenerator` / `ActionScheduler`) |

**Key distinction:** TTL/MIGRATE is a *data lifecycle* feature — retention and archiving of rows you are done with. Tasks are a *processing* feature — running business logic on a schedule. If the requirement is "when time passes, *do something* about a record," that is a task, even though TTL superficially fits.

## Deadline-Driven Events: TTL/MIGRATE vs. a Task Sweep

When the requirement is "if nothing happens to this row within N minutes, emit an event," TTL plus `MIGRATE TO TOPIC` looks like a natural fit: give the table a short TTL, and each expiring row lands on a topic as an event. The pieces do connect that way, and it is a reasonable design to consider. But TTL/MIGRATE was built for archiving, and for deadline *detection* its trade-offs usually favor a task-driven sweep:

- **Migration deletes the row from VoltDB.** The state typically needed for the follow-up action is gone, so the event must be re-ingested from the topic before anything can be done with it — an extra round trip for data that never had to leave.
- **The deadline is a column value, not business state.** Keeping a row alive through ongoing activity means updating the TTL column on every touch — an extra write whose only purpose is postponing expiration.
- **Late activity races the export.** Once migration of a row has been triggered, an UPDATE cancels the pending *delete* but **not** the already-started export — the deadline event still fires even though activity resumed in time, and the row also stays in the table (so two records eventually migrate).
- **No logic at event time.** Migration exports raw row bytes; there is no hook to run business logic when the deadline passes.

**Prefer instead:** keep the state in a normal table with a `last_updated`-style TIMESTAMP column (indexed), and sweep it with a scheduled task running a directed procedure. The procedure selects rows past the deadline, applies the business logic (or emits a proper event via an export stream), and updates or deletes the rows — all transactionally per partition. See the worked example in [ddl-auto-tasks-directed.md](ddl-auto-tasks-directed.md). When a user is weighing the TTL/MIGRATE version, present these trade-offs and confirm the direction rather than silently substituting.

TTL remains the right tool when the requirement really is "these rows stop mattering after N hours/days" — session tables, alert caches, raw event retention windows — optionally with `MIGRATE TO TARGET` when the aged data must be preserved elsewhere. One prerequisite: the TTL column must be high-cardinality (few rows sharing any one timestamp value) — see the caveat in [ddl-auto-ttl-migrate.md](ddl-auto-ttl-migrate.md).

## References

- *VoltDB Guide to Performance and Customization*: chapters on compound procedures and custom tasks
- *Using VoltDB*: "Simplifying Application Development" (tasks, directed procedures), CREATE TABLE (TTL/migration), CREATE TASK, CREATE STREAM

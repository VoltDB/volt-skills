# Analysis: Prevent PARAMETER N mispartitioning in DDL-defined procedures

## Problem

The skill generated `UpsertOrder` without `PARAMETER 1`, causing a "Mispartitioned tuple" error. The ORDERS table has `ORDER_ID` as the first column and `CUSTOMER_ID` (the partition column) as the second. VoltDB defaults to routing on parameter 0, so it routed on `ORDER_ID` instead of `CUSTOMER_ID`.

## Root cause

The Upsert template in `ddl-procedures.md` (line 66) shows:
```sql
AS UPSERT INTO [TABLE] ([PARTITION_COL], [OTHER_COL], ...) VALUES (?, ?, ...);
```

This puts partition column first — correct for a primary table but not for co-located/child tables where the table's own ID column naturally comes first (e.g., `ORDER_ID, CUSTOMER_ID, ...`). The LLM followed the established column order from the CREATE TABLE statement rather than the template's implied ordering.

The CRITICAL note about `PARAMETER N` exists (line 201) but is in a separate section, disconnected from the template being followed during generation.

## Fix: 3 changes needed

### 1. Split Upsert template into primary vs co-located cases

```sql
-- Primary table upsert (partition column IS the first column)
CREATE PROCEDURE Upsert[PrimaryTable]
    PARTITION ON TABLE [TABLE] COLUMN [PARTITION_COLUMN]
    AS UPSERT INTO [TABLE] ([PARTITION_COL], [OTHER_COL], ...) VALUES (?, ?, ...);

-- Co-located table upsert (partition column is NOT the first column)
-- PARAMETER N specifies the 0-indexed position of the partition column in the VALUES list
CREATE PROCEDURE Upsert[ColocatedTable]
    PARTITION ON TABLE [TABLE] COLUMN [PARTITION_COLUMN] PARAMETER [N]
    AS UPSERT INTO [TABLE] ([ID_COL], [PARTITION_COL], [OTHER_COL], ...) VALUES (?, ?, ...);
```

### 2. Add inline guidance at the point of generation

Move the CRITICAL note into the template block as SQL comments so it's read in context:

```sql
-- IMPORTANT: Count the ? parameters. The partition column's ? must be at position 0 (default).
-- If the partition column is NOT the first ?, add PARAMETER N where N is its 0-indexed position.
-- Example: UPSERT INTO ORDERS (ORDER_ID, CUSTOMER_ID, ...) — CUSTOMER_ID is ? at position 1
--   → PARTITION ON TABLE ORDERS COLUMN CUSTOMER_ID PARAMETER 1
```

### 3. Add post-generation verification checkpoint

After generating all DDL-defined procedures, verify each one:

> **Verification checkpoint — apply to every `CREATE PROCEDURE ... AS ...` statement:**
>
> For each DDL-defined single-partition procedure:
> 1. Identify the partition column from the `PARTITION ON TABLE ... COLUMN ...` clause
> 2. In the SQL statement, find which `?` corresponds to the partition column (0-indexed)
> 3. If it's position 0: `PARAMETER` clause is not needed (default)
> 4. If it's position N > 0: `PARAMETER N` **must** be added

### Files to change

- `ddl-procedures.md` — split template, add inline comments, add verification checkpoint section
- `SKILL.md` — add verification step in Phase 2 after DDL generation

### Summary

| Layer | What | Where |
|-------|------|-------|
| **Prevent** | Split Upsert template into primary vs co-located cases with `PARAMETER N` shown inline | `ddl-procedures.md` templates |
| **Prevent** | Move CRITICAL note into the template block as SQL comments | `ddl-procedures.md` templates |
| **Catch** | Post-generation verification checkpoint | `ddl-procedures.md` + `SKILL.md` Phase 2 |

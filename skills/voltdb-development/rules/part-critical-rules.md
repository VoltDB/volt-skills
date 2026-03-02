# Critical Partitioning Rules

> **Category:** Partitioning Strategy | **Impact:** HIGH

## Context

These 6 rules are non-negotiable. Violations cause wrong results, silent data loss, or runtime errors. Apply these rules internally when generating code — do NOT explain all rules to the user, just ensure correct output.

## Rule 1: Single Column Only

VoltDB supports ONLY single-column partition keys. NO composite partition keys.

```
✗ WRONG: PARTITION ON (CUSTOMER_ID, REGION)
✓ RIGHT: PARTITION ON CUSTOMER_ID
```

## Rule 2: Partition Key MUST Be FIRST Parameter

VoltDB routes procedure calls based on the FIRST parameter. The partition key MUST be the first parameter in `run()` and in client `callProcedureSync()` calls.

```
✓ CORRECT:
  run(long shelterId, long petId, String name, ...)
  callProcedureSync("UpsertPet", shelterId, petId, name, ...)

✗ WRONG (causes "Mispartitioned tuple" error!):
  run(long petId, String name, long shelterId, ...)
  callProcedureSync("UpsertPet", petId, name, shelterId, ...)

Why? VoltDB uses first param (petId=4) to route to partition,
but data has shelterId=1 which belongs to different partition.
```

## Rule 3: Joins Only on Partition Column

Partitioned tables can ONLY be joined correctly on the partition column. Any other join in a single-partition procedure returns PARTIAL data.

```
Tables: ORDERS (partition: CUSTOMER_ID)
        PRODUCTS (partition: PRODUCT_ID)

✗ WRONG (in single-partition proc):
  SELECT * FROM ORDERS o JOIN PRODUCTS p
  ON o.PRODUCT_ID = p.PRODUCT_ID  -- NOT partition column!
  → Returns only products in LOCAL partition = WRONG!

✓ RIGHT: Use multi-partition procedure or lookup table
```

## Rule 4: Wrong Partition = Wrong Data (Silent Failure!)

A single-partition procedure accessing a different partition key silently returns INCOMPLETE data (only local partition). VoltDB does NOT throw an error.

```
Procedure partitioned on CUSTOMER_ID = 100:
SELECT * FROM ORDERS WHERE CUSTOMER_ID = 200;
→ Returns EMPTY or partial results (not an error!)
```

## Rule 5: VoltDB Rejects Wrong-Partition Inserts

VoltDB WILL reject INSERT to wrong partition (unlike SELECT which silently fails).

```
Procedure partitioned on CUSTOMER_ID = 100:
INSERT INTO ORDERS (CUSTOMER_ID, ...) VALUES (200, ...);
→ ERROR: Mispartitioned tuple
```

## Rule 6: Replicated Tables

Tables WITHOUT a PARTITION statement are REPLICATED (copied to all nodes). Accessible from any partition.

- Use for: Reference data, lookup codes, small static tables
- Avoid for: Large tables, frequently updated data

## Procedure Type Selection

| Access Pattern | Procedure Type | Performance |
|----------------|----------------|-------------|
| Query by partition key | Single-partition | Fast |
| Join co-located tables | Single-partition | Fast |
| Query via lookup table | Single-partition | Fast |
| Search without partition key | Multi-partition | Slower |
| Cross-partition writes | Multi-partition | Slower |

## Procedure Declaration Syntax

```sql
-- Single-partition (partition key MUST be FIRST parameter):
CREATE PROCEDURE PARTITION ON TABLE X COLUMN Y
    FROM CLASS pkg.procedures.MyProc;

-- Multi-partition:
CREATE PROCEDURE FROM CLASS pkg.procedures.MyProc;
```

## Quick Reference

| Situation | Decision |
|-----------|----------|
| Column is `*_ID` with high cardinality | Good partition key |
| Column is STATUS/TYPE/FLAG | Bad — causes hot spots |
| Need to JOIN two tables | Co-locate on same partition column |
| Tables have different natural keys | Consider lookup table |
| Query includes partition key | Single-partition procedure |
| Query searches without partition key | Multi-partition procedure |
| Need cross-domain query (fast) | Create lookup table |
| Need cross-domain query (simple) | Multi-partition procedure |
| **Writing single-partition procedure** | **Partition key MUST be FIRST parameter** |
| **Calling single-partition procedure** | **Pass partition key as FIRST argument** |

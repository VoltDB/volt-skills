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

## Rule 2: Partition Key Parameter Must Match DDL Declaration

VoltDB routes procedure calls based on the parameter declared in the DDL. By default, parameter 0 (the first) is used, but you can specify any parameter position with `PARAMETER N` (0-indexed).

```
-- Default: partition key is parameter 0 (first parameter)
CREATE PROCEDURE PARTITION ON TABLE SHELTERS COLUMN SHELTER_ID
    FROM CLASS pkg.procedures.UpsertShelter;
→ run(long shelterId, String name, ...)  -- shelterId is param 0

-- Explicit PARAMETER: partition key can be ANY parameter
CREATE PROCEDURE PARTITION ON TABLE TRANSACTIONS COLUMN ACCOUNT_ID PARAMETER 0
    FROM CLASS pkg.procedures.ProcessTransaction;
→ run(long accountId, long txnId, ...)  -- accountId is param 0

-- Partition key is NOT the first parameter:
CREATE PROCEDURE PARTITION ON TABLE PETS COLUMN SHELTER_ID PARAMETER 1
    FROM CLASS pkg.procedures.UpsertPet;
→ run(long petId, long shelterId, String name, ...)  -- shelterId is param 1

Why PARAMETER matters:
VoltDB extracts the declared parameter to determine which partition
receives the call. All parameters are passed to the procedure.
If the DDL says PARAMETER 1, VoltDB uses the second argument for routing.
If omitted, PARAMETER 0 is assumed (first argument).
```

**Best practice:** Put the partition key as the first parameter when possible (simplest). Use `PARAMETER N` when the natural parameter order places it elsewhere.

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

- Use for: Reference data, lookup codes, small static tables that are **read-mostly**
- Avoid for: Large tables, frequently updated data
- **Write restriction:** Replicated tables can be READ from any procedure, but can only be WRITTEN from **multi-partition** procedures. A single-partition procedure that writes to a replicated table will fail at DDL load time.
- **Design check:** A replicated table should be written to rarely (admin operations, bulk loads) — not on every transaction. If the planned operations include frequent writes (e.g., updating stock, incrementing counters, changing status), the table should be **partitioned instead** — it is not truly reference data.

## Procedure Type Selection

| Access Pattern | Procedure Type | Performance |
|----------------|----------------|-------------|
| Query by partition key | Single-partition | Fast |
| Join co-located tables | Single-partition | Fast |
| Query via lookup table | Single-partition | Fast |
| Search without partition key | Multi-partition | Slower |
| Cross-partition writes | Multi-partition | Slower |
| **Writes to replicated table** | **Multi-partition (required)** | **Slower** |

## Procedure Declaration Syntax

```sql
-- Single-partition (partition key is first parameter by default):
CREATE PROCEDURE PARTITION ON TABLE X COLUMN Y
    FROM CLASS pkg.procedures.MyProc;

-- Single-partition (partition key at specific parameter position):
CREATE PROCEDURE PARTITION ON TABLE X COLUMN Y PARAMETER 2
    FROM CLASS pkg.procedures.MyProc;
-- → run(otherArg1, otherArg2, partitionKey, ...)  -- param 2 (0-indexed)

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
| **Writing single-partition procedure** | **Partition key position must match DDL PARAMETER N (default: 0)** |
| **Calling single-partition procedure** | **Pass partition key at the position declared in DDL** |

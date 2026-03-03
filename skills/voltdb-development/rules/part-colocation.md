# Co-locating Tables for Efficient Joins

> **Category:** Partitioning Strategy | **Impact:** HIGH

## Context

Tables partitioned on the same column **values** are co-located — their rows live on the same partition. Co-located tables can be efficiently joined in single-partition procedures. Column **names** can differ; only the values matter.

## Rules

- Tables partitioned on the same column VALUES are co-located (column names can differ)
- `CUSTOMER.ID` can join with `ORDER.CUSTOMER_ID` if values match
- Co-located tables can be efficiently joined in single-partition procedures
- If tables cannot share partition column values, use a **lookup table** instead (see `part-lookup-tables`)

## Decision Flowchart

```
START: Do tables need to be co-located?
                    │
                    ▼
         Do you need to JOIN
         these tables in
         single-partition
         procedures?
              │              │
             YES            NO
              │              │
              ▼              ▼
    Tables MUST share     Tables can have
    partition column      different partition
    VALUES (names can     columns
    differ)
              │
              ▼
    Can both tables use the SAME partition
    column values? (e.g., both use CUSTOMER_ID
    or SHELTER_ID values)
              │              │
             YES            NO
              │              │
              ▼              ▼
    CO-LOCATE:          Need LOOKUP TABLE
    PARTITION           (see part-lookup-tables)
    both tables
    on that column
              │
              ▼
    IMPORTANT: Column NAMES don't matter - VALUES do!

    Example: CUSTOMERS.ID can join with ORDERS.CUSTOMER_ID
    if partitioned on same values
```

## Example

```
  SHELTERS partitioned on shelter_id
  PETS partitioned on shelter_id (same values!)
  ✓ Can join in single-partition procedure

  ORDERS partitioned on customer_id
  PRODUCTS partitioned on product_id (different values!)
  ✗ Cannot join in single-partition procedure — need lookup table
```

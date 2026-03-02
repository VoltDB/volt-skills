# When and How to Create Lookup Tables

> **Category:** Partitioning Strategy | **Impact:** HIGH

## Context

When two tables have different partition columns (e.g., CUSTOMER_ID vs PRODUCT_ID), you cannot join them efficiently in a single-partition procedure. A lookup table denormalizes frequently-needed fields to enable single-partition access across different partition domains.

## Rules

### When to Create a Lookup Table
- Two tables have **different partition columns** (CUSTOMER_ID vs PRODUCT_ID)
- User needs to query "all X for Y" across partition domains
- Query performance is **latency-sensitive** (if not, use multi-partition procedure instead)

### How to Design a Lookup Table
- Partition the lookup table on the **query's partition column**
- Include the foreign key and any **denormalized fields** needed by the query
- Primary key should include both the partition column and the related ID
- **Trade-off:** Slower writes (must maintain lookup on insert/update), faster reads

## Decision Flowchart

```
START: Do you need a Lookup Table?
                    │
                    ▼
         Do you need to query
         "all X for Y" across
         different partition
         domains?
              │              │
             YES            NO
              │              │
              │              ▼
              │        No lookup table
              │        needed
              ▼
    Example scenarios requiring lookup:
    - "All products for customer X"
      (PRODUCTS partitioned on PRODUCT_ID,
       but need by CUSTOMER_ID)
    - "All orders for product Y"
      (ORDERS partitioned on CUSTOMER_ID,
       but need by PRODUCT_ID)
                    │
                    ▼
         Is query performance
         critical? (latency
         sensitive)
              │              │
             YES            NO
              │              │
              ▼              ▼
    CREATE              Use MULTI-PARTITION
    LOOKUP TABLE        procedure instead
    (denormalize)       (slower but simpler)
              │
              ▼
    LOOKUP TABLE PATTERN:

    CREATE TABLE CUSTOMER_PRODUCTS_LOOKUP (
        CUSTOMER_ID bigint NOT NULL,  -- partition column
        PRODUCT_ID bigint NOT NULL,
        PRODUCT_NAME varchar(100),    -- denormalized
        PRIMARY KEY (CUSTOMER_ID, PRODUCT_ID)
    );
    PARTITION TABLE CUSTOMER_PRODUCTS_LOOKUP ON COLUMN CUSTOMER_ID;

    TRADE-OFF: Slower writes (maintain lookup), faster reads
```

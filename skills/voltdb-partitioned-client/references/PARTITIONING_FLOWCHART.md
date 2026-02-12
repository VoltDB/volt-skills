# VoltDB Partitioning Decision Flowchart

A visual guide for making partitioning decisions in VoltDB.

---

## 1. Choosing a Partition Column

```
┌─────────────────────────────────────────────────────────────────┐
│                  START: Choose Partition Column                  │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │  Is column a *_ID type  │
                    │  (CUSTOMER_ID, USER_ID, │
                    │   ORDER_ID, etc.)?      │
                    └────────────────────────┘
                         │              │
                        YES            NO
                         │              │
                         ▼              ▼
              ┌──────────────┐   ┌──────────────────────┐
              │  Good start! │   │ Is it STATUS, TYPE,  │
              │  Continue... │   │ IS_ACTIVE, or similar│
              └──────────────┘   │ categorical field?   │
                     │           └──────────────────────┘
                     │                │            │
                     │               YES          NO
                     │                │            │
                     │                ▼            ▼
                     │         ┌───────────┐  ┌────────────┐
                     │         │  BAD!     │  │ Check      │
                     │         │  Low      │  │ cardinality│
                     │         │  cardinality│ │ manually   │
                     │         │  = hot spots│ └────────────┘
                     │         └───────────┘        │
                     │                              │
                     ▼                              ▼
           ┌─────────────────────────────────────────────┐
           │    Does column have HIGH CARDINALITY?       │
           │    (10x more distinct values than nodes)    │
           └─────────────────────────────────────────────┘
                         │              │
                        YES            NO
                         │              │
                         ▼              ▼
              ┌──────────────┐   ┌──────────────────────┐
              │  Continue... │   │  STOP: Find better   │
              └──────────────┘   │  column or composite │
                     │           │  business key        │
                     ▼           └──────────────────────┘
           ┌─────────────────────────────────────────────┐
           │   Is column in WHERE clause of most queries?│
           └─────────────────────────────────────────────┘
                         │              │
                        YES            NO
                         │              │
                         ▼              ▼
              ┌──────────────┐   ┌──────────────────────┐
              │  Continue... │   │ Consider: Will queries│
              └──────────────┘   │ become multi-partition│
                     │           │ (slower)? OK if rare. │
                     ▼           └──────────────────────┘
           ┌─────────────────────────────────────────────┐
           │        Is column value IMMUTABLE?           │
           │        (rarely or never changes)            │
           └─────────────────────────────────────────────┘
                         │              │
                        YES            NO
                         │              │
                         ▼              ▼
              ┌──────────────┐   ┌──────────────────────┐
              │  GOOD!       │   │  WARNING: Changing   │
              │  Use this    │   │  partition key =     │
              │  column      │   │  delete + reinsert   │
              └──────────────┘   └──────────────────────┘
```

---

## 2. Co-location Decision

```
┌─────────────────────────────────────────────────────────────────┐
│            START: Do tables need to be co-located?              │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │  Do you need to JOIN   │
                    │  these tables in       │
                    │  single-partition      │
                    │  procedures?           │
                    └────────────────────────┘
                         │              │
                        YES            NO
                         │              │
                         ▼              ▼
           ┌─────────────────────┐  ┌────────────────────┐
           │ Tables MUST share   │  │ Tables can have    │
           │ partition column    │  │ different partition│
           │ VALUES (names can   │  │ columns            │
           │ differ)             │  └────────────────────┘
           └─────────────────────┘
                     │
                     ▼
           ┌─────────────────────────────────────────────┐
           │   Can both tables use the SAME partition    │
           │   column values? (e.g., both use CUSTOMER_ID│
           │   or SHELTER_ID values)                     │
           └─────────────────────────────────────────────┘
                         │              │
                        YES            NO
                         │              │
                         ▼              ▼
              ┌──────────────┐   ┌──────────────────────┐
              │ CO-LOCATE:   │   │ Need LOOKUP TABLE    │
              │ PARTITION    │   │ (see Section 3)      │
              │ both tables  │   └──────────────────────┘
              │ on that      │
              │ column       │
              └──────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  IMPORTANT: Column NAMES don't matter - VALUES do!              │
│                                                                 │
│  Example: CUSTOMERS.ID can join with ORDERS.CUSTOMER_ID         │
│  if partitioned on same values                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Lookup Table Decision

```
┌─────────────────────────────────────────────────────────────────┐
│         START: Do you need a Lookup Table?                      │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │  Do you need to query  │
                    │  "all X for Y" across  │
                    │  different partition   │
                    │  domains?              │
                    └────────────────────────┘
                         │              │
                        YES            NO
                         │              │
                         │              ▼
                         │       ┌────────────────────┐
                         │       │ No lookup table    │
                         │       │ needed             │
                         │       └────────────────────┘
                         ▼
           ┌─────────────────────────────────────────────┐
           │  Example scenarios requiring lookup:        │
           │  • "All products for customer X"            │
           │    (PRODUCTS partitioned on PRODUCT_ID,     │
           │     but need by CUSTOMER_ID)                │
           │  • "All orders for product Y"               │
           │    (ORDERS partitioned on CUSTOMER_ID,      │
           │     but need by PRODUCT_ID)                 │
           └─────────────────────────────────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │  Is query performance  │
                    │  critical? (latency    │
                    │  sensitive)            │
                    └────────────────────────┘
                         │              │
                        YES            NO
                         │              │
                         ▼              ▼
              ┌──────────────┐   ┌──────────────────────┐
              │ CREATE       │   │ Use MULTI-PARTITION  │
              │ LOOKUP TABLE │   │ procedure instead    │
              │ (denormalize)│   │ (slower but simpler) │
              └──────────────┘   └──────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  LOOKUP TABLE PATTERN:                                          │
│                                                                 │
│  CREATE TABLE CUSTOMER_PRODUCTS_LOOKUP (                        │
│      CUSTOMER_ID bigint NOT NULL,  -- partition column          │
│      PRODUCT_ID bigint NOT NULL,                                │
│      PRODUCT_NAME varchar(100),    -- denormalized              │
│      PRIMARY KEY (CUSTOMER_ID, PRODUCT_ID)                      │
│  );                                                             │
│  PARTITION TABLE CUSTOMER_PRODUCTS_LOOKUP ON COLUMN CUSTOMER_ID;│
│                                                                 │
│  TRADE-OFF: Slower writes (maintain lookup), faster reads       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Procedure Type Selection

```
┌─────────────────────────────────────────────────────────────────┐
│         START: What type of procedure do you need?              │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │  Does your query       │
                    │  include the partition │
                    │  column in WHERE?      │
                    └────────────────────────┘
                         │              │
                        YES            NO
                         │              │
                         ▼              ▼
           ┌─────────────────────┐  ┌────────────────────┐
           │ Can be SINGLE-      │  │ MUST be MULTI-     │
           │ PARTITION           │  │ PARTITION          │
           │ (continue...)       │  │ (slower, searches  │
           └─────────────────────┘  │ all nodes)         │
                     │              └────────────────────┘
                     ▼
           ┌─────────────────────────────────────────────┐
           │   Does procedure JOIN multiple tables?      │
           └─────────────────────────────────────────────┘
                         │              │
                        YES            NO
                         │              │
                         ▼              ▼
           ┌─────────────────────┐  ┌────────────────────┐
           │ Are all joined      │  │ SINGLE-PARTITION   │
           │ tables co-located   │  │ ✓ Fast!            │
           │ (same partition     │  └────────────────────┘
           │ column values)?     │
           └─────────────────────┘
                    │         │
                   YES       NO
                    │         │
                    ▼         ▼
         ┌──────────────┐  ┌──────────────────────────────┐
         │ SINGLE-      │  │ DANGER! Join on non-partition│
         │ PARTITION    │  │ column returns WRONG results │
         │ ✓ Fast!      │  │                              │
         └──────────────┘  │ Options:                     │
                           │ 1. Use MULTI-PARTITION       │
                           │ 2. Create LOOKUP TABLE       │
                           │ 3. Restructure data model    │
                           └──────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  PROCEDURE DECLARATION:                                         │
│                                                                 │
│  Single-partition (partition key MUST be FIRST parameter):      │
│  CREATE PROCEDURE PARTITION ON TABLE X COLUMN Y                 │
│      FROM CLASS pkg.procedures.MyProc;                          │
│                                                                 │
│  Multi-partition:                                               │
│  CREATE PROCEDURE FROM CLASS pkg.procedures.MyProc;             │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  ⚠️  CRITICAL: PARAMETER ORDER IN SINGLE-PARTITION PROCEDURES   │
│                                                                 │
│  The partition key MUST be the FIRST parameter!                 │
│                                                                 │
│  Java procedure:                                                │
│    public VoltTable[] run(long shelterId, long petId, ...) {    │
│                           ▲                                     │
│                           └── Partition key FIRST!              │
│                                                                 │
│  Client call:                                                   │
│    client.callProcedure("UpsertPet", shelterId, petId, ...);    │
│                                      ▲                          │
│                                      └── Partition key FIRST!   │
│                                                                 │
│  If wrong order: "Mispartitioned tuple" error on INSERT/UPSERT  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. Critical Rules & Warnings

```
┌─────────────────────────────────────────────────────────────────┐
│                    ⚠️  CRITICAL RULES  ⚠️                        │
│               (Violations = WRONG Results!)                     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  RULE 1: Single Column Only                                     │
│  ─────────────────────────                                      │
│  VoltDB supports ONLY single-column partition keys.             │
│  NO composite partition keys (col1 + col2).                     │
│                                                                 │
│  ✗ WRONG: PARTITION ON (CUSTOMER_ID, REGION)                    │
│  ✓ RIGHT: PARTITION ON CUSTOMER_ID                              │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  RULE 2: Partition Key MUST Be FIRST Parameter                  │
│  ─────────────────────────────────────────────                  │
│  VoltDB routes procedure calls based on the FIRST parameter.    │
│  The partition key MUST be the first parameter in run().        │
│                                                                 │
│  ✓ CORRECT:                                                     │
│    run(long shelterId, long petId, String name, ...)            │
│    callProcedure("UpsertPet", shelterId, petId, name, ...)      │
│                                                                 │
│  ✗ WRONG (causes "Mispartitioned tuple" error!):                │
│    run(long petId, String name, long shelterId, ...)            │
│    callProcedure("UpsertPet", petId, name, shelterId, ...)      │
│                                                                 │
│  Why? VoltDB uses first param (petId=4) to route to partition,  │
│  but data has shelterId=1 which belongs to different partition. │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  RULE 3: Joins Only on Partition Column                         │
│  ──────────────────────────────────────                         │
│  Partitioned tables can ONLY be joined correctly on the         │
│  partition column. Any other join returns PARTIAL data!         │
│                                                                 │
│  Tables: ORDERS (partition: CUSTOMER_ID)                        │
│          PRODUCTS (partition: PRODUCT_ID)                       │
│                                                                 │
│  ✗ WRONG (in single-partition proc):                            │
│    SELECT * FROM ORDERS o JOIN PRODUCTS p                       │
│    ON o.PRODUCT_ID = p.PRODUCT_ID  -- NOT partition column!     │
│    → Returns only products in LOCAL partition = WRONG!          │
│                                                                 │
│  ✓ RIGHT: Use multi-partition or lookup table                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  RULE 4: Wrong Partition = Wrong Data (Silent Failure!)         │
│  ──────────────────────────────────────────────────────         │
│  A single-partition procedure accessing a different partition   │
│  key silently returns INCOMPLETE data (only local partition).   │
│                                                                 │
│  Procedure partitioned on CUSTOMER_ID = 100:                    │
│  SELECT * FROM ORDERS WHERE CUSTOMER_ID = 200;                  │
│  → Returns EMPTY or partial results (not an error!)             │
│                                                                 │
│  VoltDB does NOT throw an error - it just gives wrong data!     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  RULE 5: VoltDB Rejects Wrong-Partition Inserts                 │
│  ──────────────────────────────────────────────                 │
│  VoltDB WILL reject INSERT to wrong partition (unlike SELECT).  │
│                                                                 │
│  Procedure partitioned on CUSTOMER_ID = 100:                    │
│  INSERT INTO ORDERS (CUSTOMER_ID, ...) VALUES (200, ...);       │
│  → ERROR: Mispartitioned tuple                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  RULE 6: Replicated Tables                                      │
│  ────────────────────────                                       │
│  Tables WITHOUT a PARTITION statement are REPLICATED            │
│  (copied to all nodes). Accessible from any partition.          │
│                                                                 │
│  Use for: Reference data, lookup codes, small static tables     │
│  Avoid for: Large tables, frequently updated data               │
└─────────────────────────────────────────────────────────────────┘
```

---

## Quick Reference: Decision Summary

| Situation | Decision |
|-----------|----------|
| Column is `*_ID` with high cardinality | Good partition key |
| Column is STATUS/TYPE/FLAG | Bad - causes hot spots |
| Need to JOIN two tables | Co-locate on same partition column |
| Tables have different natural keys | Consider lookup table |
| Query includes partition key | Single-partition procedure |
| Query searches without partition key | Multi-partition procedure |
| Need cross-domain query (fast) | Create lookup table |
| Need cross-domain query (simple) | Multi-partition procedure |
| **Writing single-partition procedure** | **Partition key MUST be FIRST parameter** |
| **Calling single-partition procedure** | **Pass partition key as FIRST argument** |

---

## Example: Pets & Shelters

```
Data Model:
  SHELTERS: shelter_id, name, address, phone, email
  PETS: pet_id, shelter_id, name, type, adoption_status

Decision Flow:
  1. Partition column candidates:
     - shelter_id ✓ (high cardinality, in most queries)
     - pet_id ✗ (can't co-locate with shelters)
     - type ✗ (low cardinality: cats, dogs, birds)
     - adoption_status ✗ (only 4 values)

  2. Co-location:
     - SHELTERS partitioned on shelter_id
     - PETS partitioned on shelter_id (same values!)
     - ✓ Can join in single-partition procedure

  3. Procedures:
     - GetShelterWithPets → Single-partition (uses shelter_id)
     - GetPetsReadyForAdoption → Single-partition (uses shelter_id)
     - UpdatePetStatus → Single-partition (uses shelter_id)
     - SearchPetsByType → Multi-partition (no shelter_id in query)

  4. Procedure Parameter Order (CRITICAL!):

     ✓ CORRECT - UpsertPet with shelterId FIRST:
       public VoltTable[] run(long shelterId, long petId, String name, ...)
       client.callProcedure("UpsertPet", shelterId, petId, name, ...)

     ✗ WRONG - petId first causes "Mispartitioned tuple" error:
       public VoltTable[] run(long petId, String name, long shelterId, ...)
       client.callProcedure("UpsertPet", petId, name, shelterId, ...)
```

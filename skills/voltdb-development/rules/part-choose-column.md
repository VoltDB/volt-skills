# Choosing a Partition Column

> **Category:** Partitioning Strategy | **Impact:** HIGH

## Context

VoltDB distributes data across partitions based on a single column. Choosing the right partition column is the most critical design decision — it determines query performance, data distribution, and co-location opportunities.

## Rules

### Good Partition Column Candidates
- **`*_ID` columns** (CUSTOMER_ID, ORDER_ID, USER_ID) — high cardinality
- Should have **10x more distinct values** than cluster nodes
- Should appear in the **WHERE clause of most queries**
- Should be **immutable** (rarely or never changes)

### Bad Partition Column Candidates
- **STATUS, TYPE, IS_ACTIVE, COUNTRY_CODE** — low cardinality causes hot spots
- Columns that change frequently (changing partition key = delete + reinsert)
- Composite keys — VoltDB only supports **SINGLE column** partition keys

### Decision Flowchart

```
START: Choose Partition Column
         │
         ▼
   Is column a *_ID type
   (CUSTOMER_ID, USER_ID, ORDER_ID)?
         │              │
        YES            NO
         │              │
         ▼              ▼
   Good start!    Is it STATUS, TYPE,
   Continue...    IS_ACTIVE, or similar
                  categorical field?
                       │            │
                      YES          NO
                       │            │
                       ▼            ▼
                 BAD! Low      Check cardinality
                 cardinality   manually
                 = hot spots        │
                                    │
                                    ▼
         Does column have HIGH CARDINALITY?
         (10x more distinct values than nodes)
                    │              │
                   YES            NO
                    │              │
                    ▼              ▼
             Continue...     STOP: Find better
                    │        column or composite
                    ▼        business key
         Is column in WHERE clause of most queries?
                    │              │
                   YES            NO
                    │              │
                    ▼              ▼
             Continue...     Consider: Will queries
                    │        become multi-partition
                    ▼        (slower)? OK if rare.
         Is column value IMMUTABLE?
         (rarely or never changes)
                    │              │
                   YES            NO
                    │              │
                    ▼              ▼
              GOOD!          WARNING: Changing
              Use this       partition key =
              column         delete + reinsert
```

## Example

```
Data Model:
  SHELTERS: shelter_id, name, address, phone, email
  PETS: pet_id, shelter_id, name, type, adoption_status

Partition column candidates:
  - shelter_id  ✓ (high cardinality, in most queries)
  - pet_id      ✗ (can't co-locate with shelters)
  - type        ✗ (low cardinality: cats, dogs, birds)
  - adoption_status ✗ (only 4 values)
```

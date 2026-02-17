---
name: voltdb-proc-helper
description: Analyzes data models to recommend VoltDB partitioning strategies, then generates DDL schemas and stored procedures. Use when user needs partitioning advice, DDL generation, or stored procedure creation for VoltDB.
---

# VoltDB Procedure Helper

This skill analyzes a data model, recommends an optimal partitioning strategy, and generates DDL schemas and stored procedures for VoltDB.

## Capabilities

- Analyze data models and recommend partitioning strategies
- Generate DDL schemas with partition declarations
- Create stored procedures (single-partition and multi-partition)
- Design co-located table groups for efficient joins
- Suggest lookup tables for cross-partition queries

## Instructions

When invoked, follow this two-phase workflow:

### Phase 1: Partitioning Analysis

#### Step 1: Gather Data Model

Ask the user to describe their data model:
1. **Tables**: Names, columns, types, constraints
2. **Relationships**: Foreign keys, parent-child relationships
3. **Access patterns**: Common queries, which columns appear in WHERE clauses
4. **Performance priorities**: Which queries are latency-sensitive

If the user has not described a data model, use `AskUserQuestion` with:
- **question:** "What type of data model do you need?"
- **header:** "Data model"
- **options:**
  - `Describe custom tables` - I'll describe my tables and columns
  - `Use example model` - Customer/Orders/Product example
  - `Key-Value store` - Simple key-value table (no partitioning analysis needed)

If user selects "Key-Value store", skip analysis and generate a simple KEYVALUE DDL with a Put/Get procedure pair.

#### Step 2: Analyze and Recommend Partitioning Strategy

Apply the Reference Rules (at the end of this document) and the flowcharts in `references/PARTITIONING_FLOWCHART.md` to determine:

1. **Partition column** for each table (evaluate cardinality, query patterns, immutability)
2. **Co-located table groups** (tables sharing the same partition column values)
3. **Lookup tables** needed (for cross-partition domain queries)
4. **Procedure classification** (single-partition vs multi-partition for each operation)

#### Step 3: Present Strategy for Confirmation

Present the strategy to the user using `AskUserQuestion`:

Format the strategy summary as:

```
Partition Key: [COLUMN]

| Table | Partition Column | Strategy |
|-------|------------------|----------|
| TABLE1 | COLUMN | Primary entity |
| TABLE2 | COLUMN | Co-located with TABLE1 |

Why [COLUMN]?
- High cardinality (unique per [entity])
- Enables co-location of related tables
- Most queries are [entity]-centric

Procedures:
- Upsert[Table] → Single-partition (by [COLUMN])
- Get[Table]With[Related] → Single-partition (co-located join)
- Search[Table]By[Field] → Multi-partition (no partition key in query)
```

Use `AskUserQuestion` with:
- **question:** "Does this partitioning strategy work for you? [strategy summary]"
- **header:** "Strategy"
- **options:**
  - `Yes, proceed` (Recommended)
  - `Modify strategy` - I want to change something
  - `Explain more` - Tell me more about the trade-offs

---

### Phase 2: Code Generation

#### Step 4: Generate DDL Schema

**IMPORTANT:** Schema file goes at `schema/ddl.sql` (NOT in resources)

**IMPORTANT:** In VoltDB DDL, `DEFAULT` must come before `NOT NULL`:
- CORRECT: `status varchar(32) DEFAULT 'ACTIVE' NOT NULL`
- WRONG: `status varchar(32) NOT NULL DEFAULT 'ACTIVE'` (causes DDL error)

Generate `schema/ddl.sql` following this template:

```sql
-- VoltDB DDL Schema
file -inlinebatch END_OF_BATCH

-- Primary table
CREATE TABLE [TABLE_NAME] (
    [PARTITION_COLUMN] bigint NOT NULL,
    ...columns...
    PRIMARY KEY ([PARTITION_COLUMN], ...)
);
PARTITION TABLE [TABLE_NAME] ON COLUMN [PARTITION_COLUMN];

-- Co-located table (same partition key values)
CREATE TABLE [RELATED_TABLE] (
    [ID_COLUMN] bigint NOT NULL,
    [PARTITION_COLUMN] bigint NOT NULL,
    ...columns...
    PRIMARY KEY ([ID_COLUMN], [PARTITION_COLUMN])
);
PARTITION TABLE [RELATED_TABLE] ON COLUMN [PARTITION_COLUMN];

-- Lookup table (for cross-partition queries)
CREATE TABLE [TABLE1]_[TABLE2]_LOOKUP (
    [PARTITION_COLUMN] bigint NOT NULL,
    [OTHER_ID] bigint NOT NULL,
    [DENORMALIZED_FIELDS]...,
    PRIMARY KEY ([PARTITION_COLUMN], [OTHER_ID], ...)
);
PARTITION TABLE [TABLE1]_[TABLE2]_LOOKUP ON COLUMN [PARTITION_COLUMN];

-- Single-partition procedures (partition key routed)
CREATE PROCEDURE PARTITION ON TABLE [TABLE] COLUMN [PARTITION_COLUMN]
    FROM CLASS [package].procedures.[ProcedureName];

-- Multi-partition procedures (searches all nodes)
CREATE PROCEDURE FROM CLASS [package].procedures.[SearchProcedure];

END_OF_BATCH
```

For simple non-partitioned schemas (Key-Value), use:

```sql
-- VoltDB DDL Schema
file -inlinebatch END_OF_BATCH

CREATE TABLE KEYVALUE
(
    KEYNAME integer NOT NULL,
    VALUE varchar(5000) NOT NULL
);

PARTITION TABLE KEYVALUE ON COLUMN KEYNAME;

CREATE PROCEDURE FROM CLASS [package].procedures.Put;
CREATE PROCEDURE FROM CLASS [package].procedures.Get;

END_OF_BATCH
```

#### Step 5: Generate Stored Procedures

Generate Java stored procedures under `src/main/java/[package]/procedures/`.

**CRITICAL: Partition key MUST be the FIRST parameter in all single-partition procedures!**

VoltDB routes procedure calls based on the FIRST parameter value. If the partition key is not first:
- INSERT/UPSERT fails with "Mispartitioned tuple" error
- SELECT returns wrong/incomplete data (silent failure!)

**Insert/Upsert (Single-Partition) — Partition key FIRST:**
```java
package [package].procedures;

import org.voltdb.SQLStmt;
import org.voltdb.VoltProcedure;
import org.voltdb.VoltTable;

public class Upsert[Table] extends VoltProcedure {
    public final SQLStmt upsert = new SQLStmt(
        "UPSERT INTO [TABLE] ([PARTITION_COL], [OTHER_COL], ...) VALUES (?, ?, ...);"
    );

    // CRITICAL: partitionKey MUST be the FIRST parameter!
    public VoltTable[] run(long partitionKey, long otherId, String name, ...) {
        voltQueueSQL(upsert, partitionKey, otherId, name, ...);
        return voltExecuteSQL();
    }
}
```

**Get by Partition Key (Single-Partition):**
```java
public class Get[Table] extends VoltProcedure {
    public final SQLStmt get = new SQLStmt(
        "SELECT * FROM [TABLE] WHERE [PARTITION_COL] = ?;"
    );

    public VoltTable[] run(long partitionKey) {
        voltQueueSQL(get, partitionKey);
        return voltExecuteSQL();
    }
}
```

**Co-located Access (Single-Partition) — join tables sharing partition key:**
```java
public class Get[Table]With[Related] extends VoltProcedure {
    public final SQLStmt getMain = new SQLStmt(
        "SELECT * FROM [TABLE] WHERE [PARTITION_COL] = ?;");
    public final SQLStmt getRelated = new SQLStmt(
        "SELECT * FROM [RELATED] WHERE [PARTITION_COL] = ?;");

    // CRITICAL: partitionKey MUST be the FIRST parameter!
    public VoltTable[] run(long partitionKey) {
        voltQueueSQL(getMain, partitionKey);
        voltQueueSQL(getRelated, partitionKey);
        return voltExecuteSQL();
    }
}
```

**Lookup Table Access (Single-Partition):**
```java
public class Get[Table1][Table2] extends VoltProcedure {
    public final SQLStmt getLookup = new SQLStmt(
        "SELECT * FROM [TABLE1]_[TABLE2]_LOOKUP WHERE [PARTITION_COL] = ?;");

    // CRITICAL: partitionKey MUST be the FIRST parameter!
    public VoltTable[] run(long partitionKey) {
        voltQueueSQL(getLookup, partitionKey);
        return voltExecuteSQL();
    }
}
```

**Multi-Partition Search (no partition key in WHERE):**
```java
public class Search[Table]By[Field] extends VoltProcedure {
    public final SQLStmt search = new SQLStmt(
        "SELECT * FROM [TABLE] WHERE [FIELD] = ?;");

    public VoltTable[] run(String searchValue) {
        voltQueueSQL(search, searchValue);
        return voltExecuteSQL();
    }
}
```

**Simple Put/Get (for Key-Value):**
```java
package [package].procedures;

import org.voltdb.SQLStmt;
import org.voltdb.VoltProcedure;
import org.voltdb.VoltTable;

public class Put extends VoltProcedure {
    public final SQLStmt insertKey = new SQLStmt(
        "INSERT INTO KEYVALUE (KEYNAME, VALUE) VALUES (?, ?);"
    );

    public VoltTable[] run(int key, String value) {
        voltQueueSQL(insertKey, key, value);
        return voltExecuteSQL();
    }
}
```

```java
package [package].procedures;

import org.voltdb.SQLStmt;
import org.voltdb.VoltProcedure;
import org.voltdb.VoltTable;

public class Get extends VoltProcedure {
    public final SQLStmt getKey = new SQLStmt(
        "SELECT VALUE FROM KEYVALUE WHERE KEYNAME = ?;"
    );

    public VoltTable[] run(int key) {
        voltQueueSQL(getKey, key);
        return voltExecuteSQL();
    }
}
```

---

## Reference: Partitioning Rules (For Claude's Internal Use)

**Use these rules to analyze user's data model and make smart suggestions. Do NOT explain all rules to user — just apply them.**

### Choosing Partition Column
- **Good:** `*_ID` columns (CUSTOMER_ID, ORDER_ID, USER_ID) — high cardinality
- **Bad:** STATUS, TYPE, IS_ACTIVE, COUNTRY_CODE — low cardinality causes hot spots
- **Rule:** Should have 10x more distinct values than cluster nodes
- **Rule:** Should appear in WHERE clause of most queries
- **Rule:** Should be immutable (rarely changes)
- **Rule:** VoltDB only supports SINGLE column partition keys (no composite keys)

### Co-location Rules
- Tables partitioned on same column VALUES are co-located (column names can differ)
- `CUSTOMER.ID` can join with `ORDER.CUSTOMER_ID` if values match
- Co-located tables can be efficiently joined in single-partition procedures

### DDL Syntax Rules
- **DEFAULT before NOT NULL:** VoltDB requires `DEFAULT` to appear before `NOT NULL` in column definitions
  - CORRECT: `status varchar(32) DEFAULT 'ACTIVE' NOT NULL`
  - WRONG: `status varchar(32) NOT NULL DEFAULT 'ACTIVE'` (DDL error: "unexpected token: DEFAULT")

### Critical Rules (Violations = Wrong Results or Errors)

**MOST IMPORTANT — Partition Key Parameter Order:**
- The partition key MUST be the FIRST parameter in single-partition procedures
- VoltDB routes calls based on the FIRST parameter value
- If partition key is not first: INSERT/UPSERT fails with "Mispartitioned tuple" error
- If partition key is not first: SELECT returns wrong/incomplete data (silent failure!)

**Other Critical Rules:**
- Procedure can ONLY partition on an input parameter
- Partitioned table joins ONLY work correctly on partition column
- Single-partition procedure accessing different partition key returns WRONG data (only sees local partition!)
- VoltDB rejects inserts to wrong partition
- Replicated tables (no PARTITION statement) accessible from any partition

### When to Suggest Lookup Tables
- Two tables have different partition columns (CUSTOMER_ID vs PRODUCT_ID)
- User needs to query "all X for Y" across partition domains
- Denormalize frequently-needed fields
- Trade-off: Slower writes, faster reads

### Procedure Type Selection
| Access Pattern | Procedure Type | Performance |
|----------------|----------------|-------------|
| Query by partition key | Single-partition | Fast |
| Join co-located tables | Single-partition | Fast |
| Query via lookup table | Single-partition | Fast |
| Search without partition key | Multi-partition | Slower |
| Cross-partition writes | Multi-partition | Slower |

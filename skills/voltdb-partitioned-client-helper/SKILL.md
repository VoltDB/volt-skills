---
name: voltdb-partitioned-client-helper
description: Creates VoltDB client applications with custom table partitioning. Extends voltdb-min-client-helper with partition column specification, partitioned procedures, and partition-aware CRUD/search operations. Use when user wants partitioned VoltDB tables or single-partition procedures.
---

# VoltDB Partitioned Client

This skill creates VoltDB client applications with **optimized partitioning strategies**.

## How to Use This Skill

**Use the `AskUserQuestion` tool for each question. This provides clickable options for the user.**

---

## Step 1: Ask Project Name

Use `AskUserQuestion` with:
- **question:** "What should the project be called?"
- **header:** "Project name"
- **options:**
  - `my-voltdb-app` (example)
  - `voltdb-client`
  - `data-service`

User can select an option or type their own.

---

## Step 2: Ask Package Name

Use `AskUserQuestion` with:
- **question:** "What Java package should I use?"
- **header:** "Package"
- **options:**
  - `com.example.voltdb` (Recommended)
  - `com.mycompany.data`
  - `org.example.db`

---

## Step 3: Ask for Data Model

Use `AskUserQuestion` with:
- **question:** "What type of data model do you need?"
- **header:** "Data model"
- **options:**
  - `Describe custom tables` - I'll describe my tables and columns
  - `Use example model` - Customer/Orders/Product example
  - `Key-Value store` - Simple key-value table

If user selects "Describe custom tables", ask them to describe their tables in a follow-up message.

---

## Step 4: Analyze and Present Partitioning Strategy

Based on user's data model, analyze using the Reference Rules (at end of this document).

Use `AskUserQuestion` to confirm:
- **question:** "Does this partitioning strategy work for you? [show strategy summary]"
- **header:** "Confirm strategy"
- **options:**
  - `Yes, proceed` (Recommended)
  - `Modify strategy` - I want to change something
  - `Explain more` - Tell me more about the trade-offs

---

## Step 5: Ask Output Directory

Use `AskUserQuestion` with:
- **question:** "Where should I create the project?"
- **header:** "Directory"
- **options:**
  - `Current directory` (Recommended)
  - `Specify path` - I'll provide a path

---

## Step 6: Generate Project

Generate all files using templates below and from `voltdb-min-client-helper`.

**IMPORTANT: Always generate a README.md file using the README template below.**

After generating, use `AskUserQuestion`:
- **question:** "Project created. Would you like me to build and test it now?"
- **header:** "Build"
- **options:**
  - `Yes, build and test` (Recommended)
  - `No, I'll build later`
  - `Show build commands` - Just show me the commands

---

## Templates

### README.md Template (Required)

Always create a README.md file in the project root:

```markdown
# [PROJECT_NAME] - VoltDB Partitioned Client

A VoltDB client demonstrating **table partitioning and co-location** for [brief description].

## Partitioning Strategy

**Partition Key:** `[PARTITION_COLUMN]`

| Table | Partition Column | Strategy |
|-------|------------------|----------|
| [TABLE1] | [PARTITION_COL] | Primary entity |
| [TABLE2] | [PARTITION_COL] | Co-located with [TABLE1] |

### Why [PARTITION_COLUMN]?
- High cardinality (unique per [entity])
- Enables co-location of related tables
- Most queries are [entity]-centric

### Why NOT other columns?
- [LOW_CARD_COL1] - Low cardinality, causes hot spots
- [LOW_CARD_COL2] - Only N values, causes hot spots

## Procedures

| Procedure | Type | Description |
|-----------|------|-------------|
| [Proc1] | Single-partition | [description] |
| [Proc2] | Single-partition | [description] |
| [SearchProc] | Multi-partition | [description] |

## Prerequisites

- Java 17+
- Maven 3.6+
- Docker (running)
- VoltDB Enterprise license

## Build and Test

\`\`\`bash
# 1. Ensure Docker is running
docker info

# 2. Set up license
export VOLTDB_LICENSE=/path/to/license.xml

# 3. Build
mvn clean package -DskipTests

# 4. Run tests
mvn verify
\`\`\`

## Project Structure

\`\`\`
[project-name]/
├── pom.xml
├── README.md
├── schema/ddl.sql
├── src/main/java/[package]/procedures/
│   ├── [Procedure1].java
│   └── ...
└── src/test/java/[package]/
    ├── IntegrationTestBase.java
    ├── TestDataGenerator.java
    └── [TestClass]IT.java
\`\`\`
```

---

### DDL Template with Partitioning

```sql
file -inlinebatch END_OF_BATCH

-- Primary table
CREATE TABLE [TABLE_NAME] (
    [PARTITION_COLUMN] bigint NOT NULL,
    ...columns...
    PRIMARY KEY ([PARTITION_COLUMN], ...)
);
PARTITION TABLE [TABLE_NAME] ON COLUMN [PARTITION_COLUMN];

-- Co-located table (same partition key)
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

-- Single-partition procedures
CREATE PROCEDURE PARTITION ON TABLE [TABLE] COLUMN [PARTITION_COLUMN]
    FROM CLASS [package].procedures.[ProcedureName];

-- Multi-partition procedures
CREATE PROCEDURE FROM CLASS [package].procedures.[SearchProcedure];

END_OF_BATCH
```

### Procedure Templates

**CRITICAL: Partition key MUST be the FIRST parameter in all single-partition procedures!**

VoltDB routes procedure calls based on the FIRST parameter value. If the partition key is not first, inserts will fail with "Mispartitioned tuple" errors.

Use CRUD templates from `voltdb-min-client-helper`, plus:

**Insert/Upsert (Single-Partition) - Partition key FIRST:**
```java
public class Upsert[Table] extends VoltProcedure {
    public final SQLStmt upsert = new SQLStmt(
        "UPSERT INTO [TABLE] ([PARTITION_COL], [OTHER_ID], ...) VALUES (?, ?, ...);"
    );

    // CRITICAL: partitionKey MUST be the FIRST parameter!
    public VoltTable[] run(long partitionKey, long otherId, String name, ...) {
        voltQueueSQL(upsert, partitionKey, otherId, name, ...);
        return voltExecuteSQL();
    }
}
```

**Co-located Access (Single-Partition):**
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

### Test Data Generator Template

**CRITICAL: When calling procedures, pass partition key as FIRST argument!**

```java
// CORRECT: shelterId (partition key) is FIRST
client.callProcedureSync("UpsertPet", shelterId, petId, name, type, status, ...);

// WRONG: petId first will cause "Mispartitioned tuple" error!
client.callProcedureSync("UpsertPet", petId, name, type, shelterId, status, ...);
```

---

## Reference: Partitioning Rules (For Claude's Internal Use)

**Use these rules to analyze user's data model and make smart suggestions. Do NOT explain all rules to user - just apply them.**

### Choosing Partition Column
- **Good:** `*_ID` columns (CUSTOMER_ID, ORDER_ID, USER_ID) - high cardinality
- **Bad:** STATUS, TYPE, IS_ACTIVE, COUNTRY_CODE - low cardinality causes hot spots
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

**MOST IMPORTANT - Partition Key Parameter Order:**
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

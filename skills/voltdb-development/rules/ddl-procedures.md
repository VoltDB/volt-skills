# DDL Schema and Stored Procedures

> **Category:** DDL & Stored Procedures | **Impact:** HIGH

## Context

DDL and stored procedures are always generated together. Procedures come in two forms:

- **DDL-defined procedures** — single SQL statement, declared inline in `ddl.sql`. No Java class needed. Use this for any procedure that wraps a single SQL statement with no Java logic.
- **Java class procedures** — extend `VoltProcedure`, needed when a procedure has multiple SQL statements or Java logic between them (e.g., co-located access, multi-step transactions).

**Decision rule:** If a procedure has exactly one SQL statement and no Java logic, define it in DDL. Otherwise, use a Java class.

## DDL Syntax Rules

- **Schema file location:** `src/main/resources/ddl.sql` (classpath resource)
- **Remove DDL location:** `src/main/resources/remove_db.sql` (classpath resource)
- **PRIMARY KEY is REQUIRED on every table:** VoltDB requires a PRIMARY KEY for UPSERT operations. Every CREATE TABLE statement MUST include a PRIMARY KEY. Without it, UPSERT will fail with "Unsupported UPSERT table without primary key" error.
  - For primary tables: `PRIMARY KEY ([PARTITION_COLUMN])`
  - For co-located tables: `PRIMARY KEY ([PARTITION_COLUMN], [ID_COLUMN])`
  - The partition column MUST be part of the PRIMARY KEY
- **DEFAULT before NOT NULL:** VoltDB requires `DEFAULT` to appear before `NOT NULL` in column definitions
  - CORRECT: `status varchar(32) DEFAULT 'ACTIVE' NOT NULL`
  - WRONG: `status varchar(32) NOT NULL DEFAULT 'ACTIVE'` (DDL error: "unexpected token: DEFAULT")
- **DROP PROCEDURE IF EXISTS:** Every `CREATE PROCEDURE` must be preceded by a `DROP PROCEDURE ... IF EXISTS;` statement to make the DDL idempotent

## DDL Schema Template (Partitioned)

```sql
-- VoltDB DDL Schema

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

-- ============================================================
-- DDL-defined procedures (single SQL statement, no Java class)
-- ============================================================
--
-- PARAMETER N rule: VoltDB routes single-partition procedures using
-- parameter 0 (the first ?) by default. If the partition column's ?
-- is NOT at position 0, you MUST add PARAMETER N (0-indexed).
-- Getting this wrong causes "Mispartitioned tuple" on writes
-- or silent wrong results on reads.

-- Primary table upsert (partition column IS the first column → no PARAMETER needed)
DROP PROCEDURE Upsert[PrimaryTable] IF EXISTS;
CREATE PROCEDURE Upsert[PrimaryTable]
    PARTITION ON TABLE [TABLE] COLUMN [PARTITION_COLUMN]
    AS UPSERT INTO [TABLE] ([PARTITION_COL], [OTHER_COL], ...) VALUES (?, ?, ...);

-- Co-located table upsert (partition column is NOT the first column → PARAMETER N required)
-- Example: ORDERS has (ORDER_ID, CUSTOMER_ID, ...) — CUSTOMER_ID is ? at position 1
DROP PROCEDURE Upsert[ColocatedTable] IF EXISTS;
CREATE PROCEDURE Upsert[ColocatedTable]
    PARTITION ON TABLE [TABLE] COLUMN [PARTITION_COLUMN] PARAMETER [N]
    AS UPSERT INTO [TABLE] ([ID_COL], [PARTITION_COL], [OTHER_COL], ...) VALUES (?, ?, ?, ...);

-- Single-partition get by partition key
DROP PROCEDURE Get[Table] IF EXISTS;
CREATE PROCEDURE Get[Table]
    PARTITION ON TABLE [TABLE] COLUMN [PARTITION_COLUMN]
    AS SELECT * FROM [TABLE] WHERE [PARTITION_COL] = ?;

-- Single-partition lookup table access
DROP PROCEDURE Get[Table1][Table2] IF EXISTS;
CREATE PROCEDURE Get[Table1][Table2]
    PARTITION ON TABLE [TABLE1]_[TABLE2]_LOOKUP COLUMN [PARTITION_COL]
    AS SELECT * FROM [TABLE1]_[TABLE2]_LOOKUP WHERE [PARTITION_COL] = ?;

-- Multi-partition search (no partition key in WHERE — scans all nodes)
DROP PROCEDURE Search[Table]By[Field] IF EXISTS;
CREATE PROCEDURE Search[Table]By[Field]
    AS SELECT * FROM [TABLE] WHERE [FIELD] = ?;

-- ============================================================
-- Java class procedures (multiple SQL statements or Java logic)
-- Only needed for co-located access and multi-step transactions.
-- ============================================================

-- PARAMETER N is optional (0-indexed). Omit if partition key is the first parameter.
DROP PROCEDURE [package].procedures.[ProcedureName] IF EXISTS;
CREATE PROCEDURE PARTITION ON TABLE [TABLE] COLUMN [PARTITION_COLUMN]
    FROM CLASS [package].procedures.[ProcedureName];

-- If partition key is NOT the first parameter, specify its position:
-- CREATE PROCEDURE PARTITION ON TABLE [TABLE] COLUMN [PARTITION_COLUMN] PARAMETER [N]
--     FROM CLASS [package].procedures.[ProcedureName];
```

## DDL Schema Template (Key-Value)

```sql
-- VoltDB DDL Schema

CREATE TABLE KEYVALUE
(
    KEYNAME integer NOT NULL,
    VALUE varchar(5000) NOT NULL
);

PARTITION TABLE KEYVALUE ON COLUMN KEYNAME;

DROP PROCEDURE Put IF EXISTS;
CREATE PROCEDURE Put
    PARTITION ON TABLE KEYVALUE COLUMN KEYNAME
    AS UPSERT INTO KEYVALUE (KEYNAME, VALUE) VALUES (?, ?);

DROP PROCEDURE Get IF EXISTS;
CREATE PROCEDURE Get
    PARTITION ON TABLE KEYVALUE COLUMN KEYNAME
    AS SELECT VALUE FROM KEYVALUE WHERE KEYNAME = ?;
```

## Remove DDL Template (Partitioned)

The `remove_db.sql` file at `src/main/resources/remove_db.sql` drops all objects created by `ddl.sql`. **Dependency order matters:**
1. Drop procedures FIRST (they reference tables)
2. Drop lookup tables (they reference data from other tables)
3. Drop co-located/child tables (they depend on the partition design of the primary table)
4. Drop the primary table LAST

This is the reverse order of creation — what was created last is dropped first.

**Naming:** DDL-defined procedures use their short name (e.g., `Get[Table]`). Java class procedures use the fully qualified class name (e.g., `[package].procedures.[ProcedureName]`).

```sql
-- VoltDB Remove Schema — drops all objects in dependency order
-- Run this to clean up the database for a fresh start

-- Step 1: Drop procedures first (they reference tables)
-- DDL-defined procedures: use short name
DROP PROCEDURE Upsert[Table] IF EXISTS;
DROP PROCEDURE Get[Table] IF EXISTS;
DROP PROCEDURE Get[Table1][Table2] IF EXISTS;
DROP PROCEDURE Search[Table]By[Field] IF EXISTS;
-- Java class procedures: use fully qualified class name
DROP PROCEDURE [package].procedures.[ProcedureName] IF EXISTS;

-- Step 2: Drop lookup tables (they hold denormalized data from other tables)
DROP TABLE [TABLE1]_[TABLE2]_LOOKUP IF EXISTS;

-- Step 3: Drop co-located/child tables
DROP TABLE [RELATED_TABLE] IF EXISTS;

-- Step 4: Drop primary table last
DROP TABLE [TABLE_NAME] IF EXISTS;
```

## Remove DDL Template (Key-Value)

```sql
-- VoltDB Remove Schema — drops all objects in dependency order

-- Drop procedures first (DDL-defined — use short name)
DROP PROCEDURE Put IF EXISTS;
DROP PROCEDURE Get IF EXISTS;

-- Drop table
DROP TABLE KEYVALUE IF EXISTS;
```

## Stored Procedure Decision Rule

| Procedure type | # SQL statements | Java logic? | Define in |
|----------------|-----------------|-------------|-----------|
| Insert/Upsert | 1 | No | **DDL** |
| Get by partition key | 1 | No | **DDL** |
| Lookup table access | 1 | No | **DDL** |
| Multi-partition search | 1 | No | **DDL** |
| Simple Put/Get (KV) | 1 | No | **DDL** |
| Co-located access | 2+ | No | **Java class** |
| Multi-step transaction | 2+ | Yes | **Java class** |
| **Writes to replicated table** | **any** | **any** | **Must be multi-partition** |

**When ALL procedures are DDL-defined** (no co-located access or multi-step transactions):
- No `procedures/` directory needed
- No `volt-procedure-api` Maven dependency needed
- No `@UpdateClasses` call needed in `VoltDBSetup`
- No `project.jar.path` needed in `test.properties`
- No `loadClasses()` call needed in `IntegrationTestBase`

## DDL-Defined Procedure Naming

DDL-defined procedures are referenced by their short name in client code:
- `client.callProcedureAsync("Upsert[Table]", ...)`
- `client.callProcedureAsync("Get[Table]", ...)`
- `client.callProcedureAsync("Search[Table]By[Field]", ...)`

This is the same naming convention as Java class procedures — the client code is identical.

## DDL Procedure PARAMETER N Verification

**After generating all DDL-defined procedures, verify each single-partition `CREATE PROCEDURE ... AS ...` statement:**

1. Identify the partition column from the `PARTITION ON TABLE ... COLUMN ...` clause
2. In the SQL statement, find which `?` corresponds to the partition column (0-indexed)
3. If it's position 0: no `PARAMETER` clause needed (default)
4. If it's position N > 0: `PARAMETER N` **must** be present — otherwise VoltDB routes on the wrong value

**Common case requiring PARAMETER N:** Co-located/child table upserts where the table's own ID column comes before the partition column. Example:
```
UPSERT INTO ORDERS (ORDER_ID, CUSTOMER_ID, ...) VALUES (?, ?, ...)
                     ^pos 0    ^pos 1 ← partition column
→ Must add: PARAMETER 1
```

Failure to add `PARAMETER N` causes:
- **Writes:** "Mispartitioned tuple" error (hard failure)
- **Reads:** Returns wrong/incomplete data (silent failure!)

## Java Class Procedure Templates

Java class procedures go under `src/main/java/[package]/procedures/`. Only generate Java class files for procedures that require multiple SQL statements or Java logic.

**CRITICAL: Partition key parameter position must match the DDL declaration.**

VoltDB routes procedure calls based on the parameter declared in the DDL (`PARAMETER N`, 0-indexed, defaults to 0).
- If `PARAMETER N` is omitted, VoltDB uses parameter 0 (the first) for routing
- If `PARAMETER N` is specified, VoltDB uses parameter N for routing
- Mismatched routing causes: INSERT/UPSERT "Mispartitioned tuple" error, SELECT returns wrong/incomplete data (silent failure!)

### Co-located Access (Single-Partition) — join tables sharing partition key

```java
package [package].procedures;

import org.voltdb.SQLStmt;
import org.voltdb.VoltProcedure;
import org.voltdb.VoltTable;

public class Get[Table]With[Related] extends VoltProcedure {
    public final SQLStmt getMain = new SQLStmt(
        "SELECT * FROM [TABLE] WHERE [PARTITION_COL] = ?;");
    public final SQLStmt getRelated = new SQLStmt(
        "SELECT * FROM [RELATED] WHERE [PARTITION_COL] = ?;");

    // Partition key position must match DDL PARAMETER N (default: parameter 0)
    public VoltTable[] run(long partitionKey) {
        voltQueueSQL(getMain, partitionKey);
        voltQueueSQL(getRelated, partitionKey);
        return voltExecuteSQL();
    }
}
```

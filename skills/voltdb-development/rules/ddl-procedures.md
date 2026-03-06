# DDL Schema and Stored Procedures

> **Category:** DDL & Stored Procedures | **Impact:** HIGH

## Context

DDL and stored procedures are always generated together — the DDL defines tables and partition declarations, and procedure declarations reference the Java classes. This rule covers the complete DDL template, all procedure templates, and DDL syntax rules.

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

-- Single-partition procedures (partition key routed)
DROP PROCEDURE [package].procedures.[ProcedureName] IF EXISTS;
CREATE PROCEDURE PARTITION ON TABLE [TABLE] COLUMN [PARTITION_COLUMN]
    FROM CLASS [package].procedures.[ProcedureName];

-- Multi-partition procedures (searches all nodes)
DROP PROCEDURE [package].procedures.[SearchProcedure] IF EXISTS;
CREATE PROCEDURE FROM CLASS [package].procedures.[SearchProcedure];
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

DROP PROCEDURE [package].procedures.Put IF EXISTS;
CREATE PROCEDURE FROM CLASS [package].procedures.Put;

DROP PROCEDURE [package].procedures.Get IF EXISTS;
CREATE PROCEDURE FROM CLASS [package].procedures.Get;
```

## Remove DDL Template (Partitioned)

The `remove_db.sql` file at `src/main/resources/remove_db.sql` drops all objects created by `ddl.sql`. **Dependency order matters:**
1. Drop procedures FIRST (they reference tables)
2. Drop lookup tables (they reference data from other tables)
3. Drop co-located/child tables (they depend on the partition design of the primary table)
4. Drop the primary table LAST

This is the reverse order of creation — what was created last is dropped first.

```sql
-- VoltDB Remove Schema — drops all objects in dependency order
-- Run this to clean up the database for a fresh start

-- Step 1: Drop procedures first (they reference tables)
DROP PROCEDURE [package].procedures.[ProcedureName] IF EXISTS;
DROP PROCEDURE [package].procedures.[SearchProcedure] IF EXISTS;

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

-- Drop procedures first
DROP PROCEDURE [package].procedures.Put IF EXISTS;
DROP PROCEDURE [package].procedures.Get IF EXISTS;

-- Drop table
DROP TABLE KEYVALUE IF EXISTS;
```

## Stored Procedure Templates

All procedures go under `src/main/java/[package]/procedures/`.

**CRITICAL: Partition key MUST be the FIRST parameter in all single-partition procedures!**

VoltDB routes procedure calls based on the FIRST parameter value. If the partition key is not first:
- INSERT/UPSERT fails with "Mispartitioned tuple" error
- SELECT returns wrong/incomplete data (silent failure!)

### Insert/Upsert (Single-Partition) — Partition key FIRST

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

### Get by Partition Key (Single-Partition)

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

### Co-located Access (Single-Partition) — join tables sharing partition key

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

### Lookup Table Access (Single-Partition)

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

### Multi-Partition Search (no partition key in WHERE)

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

### Simple Put/Get (for Key-Value)

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

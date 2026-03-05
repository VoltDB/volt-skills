# VoltDB Development — Compiled Rules

> Auto-generated from rules/*.md — do not edit directly.

---

# DDL Schema and Stored Procedures

> **Category:** DDL & Stored Procedures | **Impact:** HIGH

## Context

DDL and stored procedures are always generated together — the DDL defines tables and partition declarations, and procedure declarations reference the Java classes. This rule covers the complete DDL template, all procedure templates, and DDL syntax rules.

## DDL Syntax Rules

- **Schema file location:** `schema/ddl.sql` (NOT in resources)
- **PRIMARY KEY is REQUIRED on every table:** VoltDB requires a PRIMARY KEY for UPSERT operations. Every CREATE TABLE statement MUST include a PRIMARY KEY. Without it, UPSERT will fail with "Unsupported UPSERT table without primary key" error.
  - For primary tables: `PRIMARY KEY ([PARTITION_COLUMN])`
  - For co-located tables: `PRIMARY KEY ([PARTITION_COLUMN], [ID_COLUMN])`
  - The partition column MUST be part of the PRIMARY KEY
- **DEFAULT before NOT NULL:** VoltDB requires `DEFAULT` to appear before `NOT NULL` in column definitions
  - CORRECT: `status varchar(32) DEFAULT 'ACTIVE' NOT NULL`
  - WRONG: `status varchar(32) NOT NULL DEFAULT 'ACTIVE'` (DDL error: "unexpected token: DEFAULT")

## DDL Schema Template (Partitioned)

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

## DDL Schema Template (Key-Value)

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

## Remove DDL Template (Partitioned)

The `remove_db.sql` file drops all objects created by `ddl.sql`. **Dependency order matters:**
1. Drop procedures FIRST (they reference tables)
2. Drop lookup tables (they reference data from other tables)
3. Drop co-located/child tables (they depend on the partition design of the primary table)
4. Drop the primary table LAST

This is the reverse order of creation — what was created last is dropped first.

```sql
-- VoltDB Remove Schema — drops all objects in dependency order
-- Run this to clean up the database for a fresh start
file -inlinebatch END_OF_BATCH

-- Step 1: Drop procedures first (they reference tables)
DROP PROCEDURE [package].procedures.[ProcedureName] IF EXISTS;
DROP PROCEDURE [package].procedures.[SearchProcedure] IF EXISTS;

-- Step 2: Drop lookup tables (they hold denormalized data from other tables)
DROP TABLE [TABLE1]_[TABLE2]_LOOKUP IF EXISTS;

-- Step 3: Drop co-located/child tables
DROP TABLE [RELATED_TABLE] IF EXISTS;

-- Step 4: Drop primary table last
DROP TABLE [TABLE_NAME] IF EXISTS;

END_OF_BATCH
```

## Remove DDL Template (Key-Value)

```sql
-- VoltDB Remove Schema — drops all objects in dependency order
file -inlinebatch END_OF_BATCH

-- Drop procedures first
DROP PROCEDURE [package].procedures.Put IF EXISTS;
DROP PROCEDURE [package].procedures.Get IF EXISTS;

-- Drop table
DROP TABLE KEYVALUE IF EXISTS;

END_OF_BATCH
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

---

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

---

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

---

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

---

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

---

# Maven Project Structure and Setup

> **Category:** Project Setup | **Impact:** MEDIUM

## Context

VoltDB client projects use Maven for build management. This rule defines the complete project structure, `pom.xml` template with all required dependencies and plugins, and build/verify instructions.

## Prerequisites

Before creating a project, the skill MUST actively verify all prerequisites (see SKILL.md Step 1 and Step 2). Do not just document them — run the checks.

Required infrastructure:
- **Docker** — installed and running (required for VoltDB testcontainer)
- **Java 17+** — installed
- **Maven 3.6+** — installed
- **VoltDB Enterprise license** — file path confirmed by the user

### Active Prerequisite Verification

The skill runs these checks at the start of every session:

```bash
# 1. Verify Docker is running (REQUIRED - tests will fail without Docker)
docker info > /dev/null 2>&1
# If this fails: ask user to start Docker
# macOS: open -a Docker
# Linux: sudo systemctl start docker

# 2. Verify Java version (must be 17+)
java -version 2>&1

# 3. Verify Maven version (must be 3.6+)
mvn -version 2>&1

# 4. Verify VoltDB license file exists (path provided by user in Step 2)
test -f "$VOLTDB_LICENSE" && echo "License found" || echo "License NOT found"
```

**IMPORTANT:** If any prerequisite fails, stop and ask the user to fix it before proceeding. Do not generate any project files until all prerequisites are confirmed.

## Project Directory Structure

```
<project-name>/
├── pom.xml
├── schema/
│   ├── ddl.sql              # Create tables, partitions, procedures
│   └── remove_db.sql        # Drop everything in correct dependency order
├── src/
│   ├── main/java/<package>/
│   │   └── procedures/
│   └── test/
│       ├── java/<package>/
│       └── resources/integration/
│           └── test.properties
└── README.md
```

## pom.xml Template

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.example</groupId>
    <artifactId><project-name></artifactId>
    <version>1.0-SNAPSHOT</version>
    <packaging>jar</packaging>

    <properties>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <maven.compiler.source>17</maven.compiler.source>
        <maven.compiler.target>17</maven.compiler.target>
        <voltdb.version>14.3.1</voltdb.version>
        <volt-testcontainer.version>1.7.0</volt-testcontainer.version>
    </properties>

    <dependencies>
        <!-- VoltDB Procedure API (for stored procedures) - provided scope.
             Note: volt-procedure-api uses a different version from voltdbclient. -->
        <dependency>
            <groupId>org.voltdb</groupId>
            <artifactId>volt-procedure-api</artifactId>
            <version>15.0.0-rc2</version>
            <scope>provided</scope>
        </dependency>
        <dependency>
            <groupId>org.voltdb</groupId>
            <artifactId>voltdbclient</artifactId>
            <version>${voltdb.version}</version>
            <scope>provided</scope>
        </dependency>

        <!-- Test dependencies -->
        <dependency>
            <groupId>org.voltdb</groupId>
            <artifactId>volt-testcontainer</artifactId>
            <version>${volt-testcontainer.version}</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter</artifactId>
            <version>5.10.0</version>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <testResources>
            <testResource>
                <directory>src/test/resources</directory>
                <filtering>false</filtering>
            </testResource>
            <testResource>
                <directory>src/test/resources/integration</directory>
                <filtering>true</filtering>
                <includes>
                    <include>**/*.properties</include>
                </includes>
            </testResource>
        </testResources>

        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-dependency-plugin</artifactId>
                <version>3.6.1</version>
                <executions>
                    <execution>
                        <id>copy-dependencies</id>
                        <phase>package</phase>
                        <goals>
                            <goal>copy-dependencies</goal>
                        </goals>
                        <configuration>
                            <outputDirectory>${project.build.directory}/lib</outputDirectory>
                            <includeScope>runtime</includeScope>
                        </configuration>
                    </execution>
                </executions>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-jar-plugin</artifactId>
                <version>3.4.2</version>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-surefire-plugin</artifactId>
                <version>3.2.5</version>
                <configuration>
                    <argLine>--add-opens=java.base/sun.nio.ch=ALL-UNNAMED</argLine>
                    <includes>
                        <include>**/*Test.java</include>
                    </includes>
                    <excludes>
                        <exclude>**/*IT.java</exclude>
                    </excludes>
                </configuration>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-failsafe-plugin</artifactId>
                <version>3.2.5</version>
                <configuration>
                    <includes>
                        <include>**/*IT.java</include>
                    </includes>
                </configuration>
                <executions>
                    <execution>
                        <goals>
                            <goal>integration-test</goal>
                            <goal>verify</goal>
                        </goals>
                    </execution>
                </executions>
            </plugin>
        </plugins>
    </build>
</project>
```

## Key Technical Details

| Item | Value |
|------|-------|
| VoltDBCluster import | `org.voltdbtest.testcontainer.VoltDBCluster` |
| Docker image | `voltdb/voltdb-enterprise:` + version |
| Schema location | `schema/ddl.sql` (NOT in resources) |
| Procedure dependency | `volt-procedure-api` (NOT `voltdb`) |
| Constructor | `new VoltDBCluster(licensePath, image, extraLibDir)` |

## Build and Verify Instructions

```bash
# 1. VERIFY DOCKER IS RUNNING (tests require Docker)
docker info
# If not running: macOS: open -a Docker | Linux: sudo systemctl start docker

# 2. SET UP VOLTDB LICENSE (if not already done)
export VOLTDB_LICENSE=/path/to/your/license.xml
# OR: cp /path/to/license.xml /tmp/voltdb-license.xml

# 3. NAVIGATE TO PROJECT DIRECTORY
cd <project-name>

# 4. BUILD THE PROJECT (compile and package without running tests)
mvn clean package -DskipTests

# 5. RUN INTEGRATION TESTS (starts VoltDB in Docker, loads schema, runs tests)
mvn verify

# EXPECTED OUTPUT ON SUCCESS:
# - Docker pulls voltdb/voltdb-enterprise image (first run only)
# - VoltDB container starts
# - JAR with stored procedures is loaded
# - DDL schema is applied
# - Test data is generated and verified
# - Container shuts down
# - BUILD SUCCESS message

# TROUBLESHOOTING:
# "Cannot connect to Docker daemon" -> Start Docker: open -a Docker (macOS)
# "License file not found" -> Check VOLTDB_LICENSE env var or /tmp/voltdb-license.xml
# "Schema file not found" -> Ensure schema/ddl.sql exists in project root
# "Connection refused" -> Wait for Docker to fully start, then retry
```

---

# IntegrationTestBase Template

> **Category:** Integration Testing | **Impact:** MEDIUM

## Context

The `IntegrationTestBase` class provides dual-mode VoltDB connectivity for integration tests: **testcontainer** mode (starts a Docker container automatically) and **external** mode (connects to a running VoltDB instance). All integration test classes extend this base.

## Template

Create `src/test/java/[package]/IntegrationTestBase.java`:

```java
package [package];

import org.voltdb.client.Client2;
import org.voltdb.client.Client2Config;
import org.voltdb.client.ClientFactory;
import org.voltdb.client.ClientResponse;
import org.voltdbtest.testcontainer.VoltDBCluster;

import java.io.File;
import java.io.FileFilter;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Arrays;
import java.util.Properties;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

public class IntegrationTestBase {

    private static final Properties props = new Properties();

    static {
        try (InputStream input = IntegrationTestBase.class.getClassLoader()
                .getResourceAsStream("test.properties")) {
            if (input != null) {
                props.load(input);
            }
        } catch (IOException e) {
            // Use defaults
        }
    }

    public String getImageVersion() {
        return props.getProperty("voltdb.image.version", "14.3.1");
    }

    /**
     * Returns the test mode: "testcontainer" (default) or "external".
     */
    public String getTestMode() {
        return props.getProperty("voltdb.test.mode", "testcontainer");
    }

    /**
     * Returns true if tests should start a VoltDB testcontainer.
     */
    public boolean isTestContainerMode() {
        return "testcontainer".equalsIgnoreCase(getTestMode());
    }

    /**
     * Returns true if the testcontainer should be shut down after tests complete.
     * Only relevant in testcontainer mode. Default: true.
     */
    public boolean isShutdownOnCompletion() {
        return Boolean.parseBoolean(
            props.getProperty("voltdb.testcontainer.shutdown", "true"));
    }

    /**
     * Returns the external VoltDB host. Default: localhost.
     */
    public String getExternalHost() {
        return props.getProperty("voltdb.external.host", "localhost");
    }

    /**
     * Returns the external VoltDB port. Default: 21211.
     */
    public int getExternalPort() {
        return Integer.parseInt(
            props.getProperty("voltdb.external.port", "21211"));
    }

    /**
     * Creates a VoltDBCluster testcontainer instance (not yet started).
     */
    public VoltDBCluster createTestContainer() {
        return new VoltDBCluster(
            getLicensePath(),
            "voltdb/voltdb-enterprise:" + getImageVersion(),
            getExtraLibDirectory()
        );
    }

    /**
     * Creates a Client2 connection to an external VoltDB instance.
     */
    public Client2 createExternalClient() throws Exception {
        Client2Config config = new Client2Config();
        Client2 client = ClientFactory.createClient(config);
        String host = getExternalHost();
        int port = getExternalPort();
        System.out.println("Connecting to external VoltDB at " + host + ":" + port);
        client.connectSync(host, port);
        return client;
    }

    /**
     * Loads procedure JARs and applies DDL schema on an external VoltDB instance
     * using Client2 system procedures (@UpdateClasses and @AdHoc).
     */
    public void configureExternalInstance(Client2 client) {
        try {
            ClientResponse response;
            File[] jars = getJars();
            if (jars != null) {
                for (File jarToLoad : jars) {
                    System.out.println("Loading classes from: " + jarToLoad);
                    byte[] jarBytes = Files.readAllBytes(jarToLoad.toPath());
                    response = client.callProcedureSync("@UpdateClasses", jarBytes, null);
                    assertEquals(ClientResponse.SUCCESS, response.getStatus(),
                        "Load classes must pass");
                }
            }

            String basedir = System.getProperty("user.dir");
            File schemaFile = new File(basedir, "schema/ddl.sql");
            if (schemaFile.exists()) {
                System.out.println("Loading schema from: " + schemaFile.getAbsolutePath());
                String ddl = new String(Files.readAllBytes(schemaFile.toPath()));
                // Strip sqlcmd batch directives
                ddl = ddl.replace("file -inlinebatch END_OF_BATCH", "")
                          .replace("END_OF_BATCH", "");
                for (String stmt : ddl.split(";")) {
                    stmt = stmt.trim();
                    if (!stmt.isEmpty() && !stmt.startsWith("--")) {
                        response = client.callProcedureSync("@AdHoc", stmt + ";");
                        assertEquals(ClientResponse.SUCCESS, response.getStatus(),
                            "DDL statement must pass: " + stmt);
                    }
                }
            } else {
                System.err.println("Schema file not found at: " + schemaFile.getAbsolutePath());
            }
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    /**
     * Starts the testcontainer, loads procedure JARs, and applies the DDL schema.
     */
    public void configureTestContainer(VoltDBCluster db) {
        try {
            db.start();
            ClientResponse response;
            File[] jars = getJars();
            if (jars != null) {
                for (File jarToLoad : jars) {
                    System.out.println("Loading classes from: " + jarToLoad);
                    response = db.loadClasses(jarToLoad.getAbsolutePath());
                    assertEquals(ClientResponse.SUCCESS, response.getStatus(),
                        "Load classes must pass");
                }
            }

            String basedir = System.getProperty("user.dir");
            File schemaFile = new File(basedir, "schema/ddl.sql");
            if (schemaFile.exists()) {
                System.out.println("Loading schema from: " + schemaFile.getAbsolutePath());
                assertTrue(db.runDDL(schemaFile), "Schema must get loaded");
            } else {
                System.err.println("Schema file not found at: " + schemaFile.getAbsolutePath());
            }
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    /**
     * Shuts down the testcontainer only if shutdown-on-completion is enabled.
     * In external mode or when shutdown is disabled, this is a no-op.
     */
    public void shutdownIfNeeded(VoltDBCluster db) {
        if (db != null && isShutdownOnCompletion()) {
            System.out.println("Shutting down VoltDB testcontainer...");
            db.shutdown();
        } else if (db != null) {
            System.out.println("Keeping VoltDB testcontainer running (shutdown disabled).");
        }
    }

    protected String getExtraLibDirectory() {
        String basedir = System.getProperty("user.dir");
        File libdir = new File(basedir, "target/lib");
        if (libdir.exists() && libdir.isDirectory() &&
            Arrays.stream(libdir.listFiles())
                .anyMatch(file -> file.getName().toLowerCase().endsWith(".jar"))) {
            return libdir.getAbsolutePath();
        }
        return null;
    }

    protected File[] getJars() {
        String relPath = getClass().getProtectionDomain()
            .getCodeSource().getLocation().getFile();
        File targetDir = new File(relPath + "/../");
        FileFilter jarFiles = pathname -> {
            if (pathname.isDirectory()) return false;
            String name = pathname.getName();
            return name.endsWith(".jar") && !name.startsWith("original");
        };
        return targetDir.listFiles(jarFiles);
    }

    protected String getLicensePath() {
        // 1. Check VOLTDB_LICENSE environment variable
        String envLicense = System.getenv("VOLTDB_LICENSE");
        if (envLicense != null) {
            File file = Paths.get(envLicense).toAbsolutePath().toFile();
            if (file.exists()) {
                System.out.println("License file path is: " + file.getAbsolutePath());
                return file.getAbsolutePath();
            }
            // Env var is set but points to a missing file
            throw new IllegalStateException(
                "VoltDB license file not found!\n\n"
                + "  VOLTDB_LICENSE is set to: " + envLicense + "\n"
                + "  Resolved path: " + file.getAbsolutePath() + "\n"
                + "  But this file does not exist.\n\n"
                + "Fix options:\n"
                + "  1. Correct the path:  export VOLTDB_LICENSE=/actual/path/to/license.xml\n"
                + "  2. Copy your license: cp /path/to/license.xml " + file.getAbsolutePath() + "\n"
            );
        }

        // 2. Fall back to default location
        String defaultPath = "/tmp/voltdb-license.xml";
        File defaultFile = new File(defaultPath);
        if (defaultFile.exists()) {
            System.out.println("License file path is: " + defaultPath);
            return defaultPath;
        }

        // 3. Neither option found — fail with actionable message
        throw new IllegalStateException(
            "VoltDB license file not found!\n\n"
            + "  Checked:\n"
            + "    - VOLTDB_LICENSE env var: (not set)\n"
            + "    - Default location: " + defaultPath + " (not found)\n\n"
            + "Fix options:\n"
            + "  1. Set environment variable:  export VOLTDB_LICENSE=/path/to/license.xml\n"
            + "  2. Copy to default location:  cp /path/to/license.xml " + defaultPath + "\n"
        );
    }
}
```

## Key Details

| Item | Value |
|------|-------|
| VoltDBCluster import | `org.voltdbtest.testcontainer.VoltDBCluster` |
| Client API | `db.getClient2()` returns `Client2` |
| Test mode property | `voltdb.test.mode` = `testcontainer` or `external` |
| Shutdown property | `voltdb.testcontainer.shutdown` = `true` or `false` |

---

# TestDataGenerator, IT Test Class, and Test Configuration

> **Category:** Integration Testing | **Impact:** MEDIUM

## Context

This rule covers all schema-dependent test artifacts that get generated together: the test data generator, the integration test class, test.properties configuration, and run instructions.

## TestDataGenerator Template

Create `src/test/java/[package]/TestDataGenerator.java`.

The generator must be **schema-aware**: generate appropriate data for each column type and table in the DDL. Use Client2 API to call stored procedures.

**CRITICAL: When calling single-partition procedures, pass partition key as FIRST argument!**

```java
// CORRECT: partitionKey (e.g., shelterId) is FIRST
client.callProcedureSync("UpsertPet", shelterId, petId, name, type, status);

// WRONG: petId first causes "Mispartitioned tuple" error!
client.callProcedureSync("UpsertPet", petId, name, type, shelterId, status);
```

### Key-Value Schema Template

```java
package [package];

import org.voltdb.client.Client2;
import org.voltdb.client.ClientResponse;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

/**
 * Generates test data for the KEYVALUE table.
 * Customize this class to generate data for your specific schema.
 */
public class TestDataGenerator {

    private final Client2 client;
    private final Random random = new Random();

    // Sample values for generating test data
    private static final String[] SAMPLE_VALUES = {
        "Hello World",
        "VoltDB Test Data",
        "Integration Testing",
        "Key-Value Store",
        "High Performance",
        "In-Memory Database",
        "ACID Transactions",
        "Low Latency",
        "Scalable Solution",
        "Real-Time Analytics"
    };

    public TestDataGenerator(Client2 client) {
        this.client = client;
    }

    /**
     * Generates and inserts test data into the KEYVALUE table.
     * @param count Number of records to generate
     * @return List of keys that were inserted
     */
    public List<Integer> generateTestData(int count) throws Exception {
        List<Integer> insertedKeys = new ArrayList<>();

        System.out.println("========================================");
        System.out.println("GENERATING TEST DATA");
        System.out.println("========================================");

        for (int i = 1; i <= count; i++) {
            int key = i;
            String value = SAMPLE_VALUES[random.nextInt(SAMPLE_VALUES.length)] + " #" + i;

            ClientResponse response = client.callProcedureSync("Put", key, value);
            if (response.getStatus() == ClientResponse.SUCCESS) {
                insertedKeys.add(key);
                System.out.printf("Inserted: key=%d, value='%s'%n", key, value);
            } else {
                System.err.printf("Failed to insert key=%d: %s%n", key, response.getStatusString());
            }
        }

        System.out.println("----------------------------------------");
        System.out.printf("Total records inserted: %d%n", insertedKeys.size());
        System.out.println("========================================");

        return insertedKeys;
    }

    /**
     * Queries and prints all data for the given keys.
     * @param keys List of keys to query
     */
    public void queryAndPrintData(List<Integer> keys) throws Exception {
        System.out.println();
        System.out.println("========================================");
        System.out.println("QUERYING TEST DATA");
        System.out.println("========================================");

        int successCount = 0;
        for (Integer key : keys) {
            ClientResponse response = client.callProcedureSync("Get", key);
            if (response.getStatus() == ClientResponse.SUCCESS) {
                org.voltdb.VoltTable table = response.getResults()[0];
                if (table.advanceRow()) {
                    String value = table.getString(0);
                    System.out.printf("Retrieved: key=%d, value='%s'%n", key, value);
                    successCount++;
                } else {
                    System.out.printf("No data found for key=%d%n", key);
                }
            } else {
                System.err.printf("Failed to query key=%d: %s%n", key, response.getStatusString());
            }
        }

        System.out.println("----------------------------------------");
        System.out.printf("Total records retrieved: %d / %d%n", successCount, keys.size());
        System.out.println("========================================");
    }
}
```

### Partitioned Schema Guidelines

For partitioned schemas, adapt the generator to:
1. Generate data for each table in insertion order (parent tables first)
2. Use realistic sample data arrays per column type (names, statuses, dates, etc.)
3. Maintain referential integrity (use generated parent IDs for child records)
4. Pass partition key as FIRST argument in all procedure calls
5. Include methods for each table: `generate[Table]Data(int count)`
6. Include query/print methods for each read procedure

## Integration Test Class Template

Create `src/test/java/[package]/[TestName]IT.java`.

The test class supports both testcontainer and external modes via the base class helper methods.

```java
package [package];

import org.junit.jupiter.api.Test;
import org.voltdb.client.Client2;
import org.voltdb.client.ClientResponse;
import org.voltdb.VoltTable;
import org.voltdbtest.testcontainer.VoltDBCluster;

import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

public class [TestName]IT extends IntegrationTestBase {

    private static final int TEST_DATA_COUNT = 10;

    @Test
    public void test[Scenario]() {
        VoltDBCluster db = null;
        try {
            Client2 client;
            if (isTestContainerMode()) {
                db = createTestContainer();
                configureTestContainer(db);
                client = db.getClient2();
            } else {
                client = createExternalClient();
                configureExternalInstance(client);
            }

            // Use TestDataGenerator to insert test data
            TestDataGenerator generator = new TestDataGenerator(client);
            // Generate data for all tables
            generator.generateTestData(TEST_DATA_COUNT);

            // ============================================
            // Verify CRUD operations
            // ============================================

            // Test insert/upsert
            // [Call upsert procedure, verify SUCCESS response]

            // Test get by partition key
            // [Call get procedure, verify returned data matches inserted data]

            // Test co-located access (if applicable)
            // [Call co-located procedure, verify both result tables have data]

            // ============================================
            // Verify search operations
            // ============================================

            // Test search by non-partition field (multi-partition)
            // [Call search procedure, verify results across partitions]

            // Test lookup table access (if applicable)
            // [Call lookup procedure, verify denormalized data]

            // ============================================
            // Verify edge cases
            // ============================================

            // Test get with non-existent key
            // [Call get procedure, verify empty result set]

        } catch (Exception e) {
            throw new RuntimeException(e);
        } finally {
            shutdownIfNeeded(db);
        }
    }
}
```

### Test Verification Patterns

- Insert N records via generator, assert all succeed
- Query each inserted record, assert data matches
- For co-located procedures: verify multiple result tables returned
- For multi-partition searches: verify results span data from multiple insert batches
- For lookup tables: verify denormalized fields match source data
- Edge cases: non-existent keys return empty results (not errors)

## test.properties Template

Create `src/test/resources/integration/test.properties`:

```properties
voltdb.image.version=${voltdb.version}

# VoltDB test mode: "testcontainer" (default) or "external"
voltdb.test.mode=testcontainer

# External VoltDB connection settings (used when voltdb.test.mode=external)
voltdb.external.host=localhost
voltdb.external.port=21211

# Testcontainer shutdown behavior (used when voltdb.test.mode=testcontainer)
# Set to "false" to keep the container running after tests for debugging
voltdb.testcontainer.shutdown=true
```

## Run Instructions

### Testcontainer mode (default)

```bash
# 1. VERIFY DOCKER IS RUNNING (tests require Docker)
docker info

# 2. SET UP VOLTDB LICENSE (if not already done)
export VOLTDB_LICENSE=/path/to/your/license.xml

# 3. BUILD THE PROJECT (compile and package, needed for procedure JARs)
mvn clean package -DskipTests

# 4. RUN INTEGRATION TESTS
mvn verify

# EXPECTED OUTPUT ON SUCCESS:
# - Docker pulls voltdb/voltdb-enterprise image (first run only)
# - VoltDB container starts
# - JAR with stored procedures is loaded
# - DDL schema is applied
# - Test data is generated and inserted
# - All query scenarios verified
# - Container shuts down (unless voltdb.testcontainer.shutdown=false)
# - BUILD SUCCESS message

# TROUBLESHOOTING:
# "Cannot connect to Docker daemon" -> Start Docker: open -a Docker (macOS)
# "License file not found" -> Check VOLTDB_LICENSE env var or /tmp/voltdb-license.xml
# "Schema file not found" -> Ensure schema/ddl.sql exists in project root
# "Connection refused" -> Wait for Docker to fully start, then retry
# "Load classes must pass" -> Run "mvn clean package -DskipTests" first
```

### External mode

```bash
# 1. ENSURE VOLTDB IS RUNNING at the configured host/port
# 2. BUILD THE PROJECT
mvn clean package -DskipTests

# 3. RUN INTEGRATION TESTS
mvn verify

# NOTE: Docker is NOT required in external mode.
# Tests connect directly to the running VoltDB instance
# and load classes via @UpdateClasses and schema via @AdHoc.
```

## Key Technical Details

| Item | Value |
|------|-------|
| Client API | `db.getClient2()` returns `Client2` |
| Procedure calls | `client.callProcedureSync(procName, args...)` |
| Result parsing | `response.getResults()[0]`, `table.advanceRow()`, `table.getString(col)` |
| Test naming | `*IT.java` suffix (picked up by maven-failsafe-plugin) |

---

# README.md Generation Template

> **Category:** Workflow & Templates | **Impact:** MEDIUM

## Context

Every generated VoltDB client project should include a README.md documenting the partitioning strategy, procedures, prerequisites, and build instructions. This template is filled in based on the analysis and generation results.

## Template

**IMPORTANT: Always generate a README.md file in the project root using this template:**

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
├── schema/
│   ├── ddl.sql              # Create tables, partitions, procedures
│   └── remove_db.sql        # Drop everything (for iteration/cleanup)
├── src/main/java/[package]/procedures/
│   ├── [Procedure1].java
│   └── ...
└── src/test/java/[package]/
    ├── IntegrationTestBase.java
    ├── TestDataGenerator.java
    └── [TestClass]IT.java
\`\`\`

## Schema Management

- **`schema/ddl.sql`** — Creates all tables, partition declarations, and procedure registrations
- **`schema/remove_db.sql`** — Drops everything in the correct dependency order (procedures first, then tables). Use this to clean up for a fresh start or when iterating on your schema design
```

## For Key-Value Projects

Simplify the README by removing the partitioning strategy section and procedure table. Focus on:
- Project description
- Prerequisites
- Build and test commands
- Project structure


---
name: voltdb-it-tests-helper
description: Generates integration tests for VoltDB client applications using VoltDB Enterprise Docker testcontainer. Creates test base class, realistic test data generators, and integration test classes. Use when user needs VoltDB integration tests, test data generation, or testcontainer setup.
---

# VoltDB Integration Tests Helper

This skill generates integration tests for VoltDB client applications. Tests use the [volt-testcontainer](https://github.com/VoltDB/volt-testcontainer) library to run VoltDB Enterprise in Docker.

## Capabilities

- Generate `IntegrationTestBase.java` with VoltDBCluster lifecycle management
- Generate schema-aware `TestDataGenerator.java` with realistic data
- Generate integration test classes (`*IT.java`) that verify all procedures
- Generate `test.properties` for Maven resource filtering
- Support both simple and partitioned schemas

## Prerequisites

Before running generated tests:
- **Docker** is installed and running (required for VoltDB testcontainer)
- **Java 17+** is installed
- **Maven 3.6+** is installed
- **VoltDB Enterprise license** file is available
- Project is built with `mvn clean package -DskipTests` (so procedure JARs exist)

## Instructions

When invoked, follow this workflow:

### Step 1: Understand the Project Context

Determine what already exists:
1. **DDL schema** (`schema/ddl.sql`) — what tables and columns exist?
2. **Stored procedures** (`src/main/java/[package]/procedures/`) — what operations are available?
3. **Partitioning** — which tables are partitioned, on which columns?
4. **Package name** — Java package used in the project

If these don't exist yet, advise the user to use `voltdb-proc-helper` first to generate DDL and procedures.

### Step 2: Generate IntegrationTestBase.java

Create `src/test/java/[package]/IntegrationTestBase.java`:

```java
package [package];

import org.voltdb.client.ClientResponse;
import org.voltdbtest.testcontainer.VoltDBCluster;

import java.io.File;
import java.io.FileFilter;
import java.io.IOException;
import java.io.InputStream;
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
        String licensePath = "/tmp/voltdb-license.xml";
        String envLicense = System.getenv("VOLTDB_LICENSE");
        if (envLicense != null) {
            File file = Paths.get(envLicense).toAbsolutePath().toFile();
            if (file.exists()) {
                licensePath = file.getAbsolutePath();
            }
        }
        System.out.println("License file path is: " + licensePath);
        return licensePath;
    }
}
```

### Step 3: Generate TestDataGenerator.java

Create `src/test/java/[package]/TestDataGenerator.java`.

The generator must be **schema-aware**: generate appropriate data for each column type and table in the DDL. Use Client2 API to call stored procedures.

**CRITICAL: When calling single-partition procedures, pass partition key as FIRST argument!**

```java
// CORRECT: partitionKey (e.g., shelterId) is FIRST
client.callProcedureSync("UpsertPet", shelterId, petId, name, type, status);

// WRONG: petId first causes "Mispartitioned tuple" error!
client.callProcedureSync("UpsertPet", petId, name, type, shelterId, status);
```

**Template for simple Key-Value schema:**

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

**For partitioned schemas**, adapt the generator to:
1. Generate data for each table in insertion order (parent tables first)
2. Use realistic sample data arrays per column type (names, statuses, dates, etc.)
3. Maintain referential integrity (use generated parent IDs for child records)
4. Pass partition key as FIRST argument in all procedure calls
5. Include methods for each table: `generate[Table]Data(int count)`
6. Include query/print methods for each read procedure

### Step 4: Generate Integration Test Class

Create `src/test/java/[package]/[TestName]IT.java`:

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
        VoltDBCluster db = new VoltDBCluster(
            getLicensePath(),
            "voltdb/voltdb-enterprise:" + getImageVersion(),
            getExtraLibDirectory()
        );
        try {
            configureTestContainer(db);
            Client2 client = db.getClient2();

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
            if (db != null) {
                db.shutdown();
            }
        }
    }
}
```

**Test verification patterns to include:**
- Insert N records via generator, assert all succeed
- Query each inserted record, assert data matches
- For co-located procedures: verify multiple result tables returned
- For multi-partition searches: verify results span data from multiple insert batches
- For lookup tables: verify denormalized fields match source data
- Edge cases: non-existent keys return empty results (not errors)

### Step 5: Generate test.properties

Create `src/test/resources/integration/test.properties`:
```properties
voltdb.image.version=${voltdb.version}
```

### Step 6: Provide Run Instructions

```bash
# 1. VERIFY DOCKER IS RUNNING (tests require Docker)
docker info

# 2. SET UP VOLTDB LICENSE (if not already done)
export VOLTDB_LICENSE=/path/to/your/license.xml
# OR: cp /path/to/license.xml /tmp/voltdb-license.xml

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
# - Container shuts down
# - BUILD SUCCESS message

# TROUBLESHOOTING:
# "Cannot connect to Docker daemon" -> Start Docker: open -a Docker (macOS)
# "License file not found" -> Check VOLTDB_LICENSE env var or /tmp/voltdb-license.xml
# "Schema file not found" -> Ensure schema/ddl.sql exists in project root
# "Connection refused" -> Wait for Docker to fully start, then retry
# "Load classes must pass" -> Run "mvn clean package -DskipTests" first
```

## Key Technical Details

| Item | Value |
|------|-------|
| VoltDBCluster import | `org.voltdbtest.testcontainer.VoltDBCluster` |
| Docker image | `voltdb/voltdb-enterprise:` + version |
| Schema location | `schema/ddl.sql` (NOT in resources) |
| Constructor | `new VoltDBCluster(licensePath, image, extraLibDir)` |
| Client API | `db.getClient2()` returns `Client2` |
| Procedure calls | `client.callProcedureSync(procName, args...)` |
| Result parsing | `response.getResults()[0]`, `table.advanceRow()`, `table.getString(col)` |
| Test naming | `*IT.java` suffix (picked up by maven-failsafe-plugin) |

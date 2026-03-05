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
export VOLTDB_LICENSE=/path/to/voltdb-license.xml

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

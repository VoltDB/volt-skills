# CsvDataLoader, CSV Data, IT Test Class, and Test Configuration

> **Category:** Integration Testing | **Impact:** MEDIUM

## Context

This rule covers all schema-dependent test artifacts that get generated together: the CSV data loader, CSV data files, the integration test class, test.properties configuration, and run instructions.

## CsvDataLoader.java Template

Create `src/main/java/[package]/CsvDataLoader.java`:

The loader reads CSV data from classpath resources and inserts it via the `[AppName]App` methods. It lives in `src/main` (not `src/test`) because it is also used by the main app's `main()` method.

```java
package [package];

import org.voltdb.types.TimestampType;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.List;

public class CsvDataLoader {

    private static final SimpleDateFormat DATE_FORMAT =
        new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");

    // One load method per table.
    // Reads CSV, calls the appropriate app method, returns list of IDs.

    public List<Long> load[PrimaryTable]Data([AppName]App app, String resourcePath)
            throws Exception {
        List<Long> ids = new ArrayList<>();
        try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(getResource(resourcePath)))) {
            String line = reader.readLine(); // skip header
            while ((line = reader.readLine()) != null) {
                line = line.trim();
                if (line.isEmpty()) continue;
                String[] fields = parseCsvLine(line);
                // Parse fields and call app.upsert[PrimaryTable](...)
                // Example:
                // long id = Long.parseLong(fields[0].trim());
                // String name = fields[1].trim();
                // app.upsert[PrimaryTable](id, name, ...);
                // ids.add(id);
                // System.out.printf("Loaded [entity]: id=%d, name='%s'%n", id, name);
            }
        }
        System.out.printf("Total [entities] loaded: %d%n", ids.size());
        return ids;
    }

    public List<Long> load[ColocatedTable]Data([AppName]App app, String resourcePath)
            throws Exception {
        List<Long> ids = new ArrayList<>();
        try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(getResource(resourcePath)))) {
            String line = reader.readLine(); // skip header
            while ((line = reader.readLine()) != null) {
                line = line.trim();
                if (line.isEmpty()) continue;
                String[] fields = parseCsvLine(line);
                // Parse fields including timestamps:
                // TimestampType ts = new TimestampType(
                //     DATE_FORMAT.parse(fields[N].trim()).getTime() * 1000);
                // app.upsert[ColocatedTable](partitionKey, id, ..., ts, ...);
                // ids.add(id);
            }
        }
        System.out.printf("Total [co-located entities] loaded: %d%n", ids.size());
        return ids;
    }

    public String[] parseCsvLine(String line) {
        List<String> fields = new ArrayList<>();
        StringBuilder current = new StringBuilder();
        boolean inQuotes = false;
        for (int i = 0; i < line.length(); i++) {
            char c = line.charAt(i);
            if (c == '"') {
                inQuotes = !inQuotes;
            } else if (c == ',' && !inQuotes) {
                fields.add(current.toString());
                current = new StringBuilder();
            } else {
                current.append(c);
            }
        }
        fields.add(current.toString());
        return fields.toArray(new String[0]);
    }

    private InputStream getResource(String resourcePath) {
        InputStream is = getClass().getClassLoader().getResourceAsStream(resourcePath);
        if (is == null) {
            throw new RuntimeException("Resource not found: " + resourcePath);
        }
        return is;
    }
}
```

**Customization notes:**
- One `load[Table]Data()` method per table
- Parse fields based on the DDL column types
- For `timestamp` columns, use `SimpleDateFormat` → `TimestampType` conversion
- **CRITICAL:** When calling app upsert methods, pass partition key as FIRST argument

## CSV Data File Guidelines

Generate CSV data files in `src/main/resources/data/`:

### File naming
- One CSV file per table: `[table_name_lowercase].csv`
- Example: `src/main/resources/data/customers.csv`, `src/main/resources/data/orders.csv`

### Data requirements
- **Header row:** column names matching DDL column names
- **Primary entity table:** 5 rows with realistic domain data
- **Co-located entity table:** 15 rows (3 per primary entity), distributed across all primary entities
- **Timestamp format:** `yyyy-MM-dd HH:mm:ss`
- **Quoted fields:** Use double quotes for values containing commas

### Example: Primary entity CSV

```csv
customer_id,name,address,tier
1,Sarah Mitchell,"123 Oak Lane, Portland, OR",gold
2,James Cooper,"456 Maple Ave, Seattle, WA",silver
3,Emily Rodriguez,"789 Pine St, Denver, CO",bronze
4,Michael Chen,"321 Elm Rd, Austin, TX",gold
5,Lisa Thompson,"654 Cedar Blvd, Boise, ID",silver
```

### Example: Co-located entity CSV

```csv
order_id,customer_id,product,order_date,status,amount,shipping_address
1,1,Widget A,2024-06-15 10:30:00,PENDING,29.99,"123 Oak Lane, Portland, OR"
2,1,Widget B,2024-06-10 14:00:00,SHIPPED,49.99,"123 Oak Lane, Portland, OR"
3,1,Gadget C,2024-06-20 09:15:00,PENDING,19.99,"123 Oak Lane, Portland, OR"
4,2,Widget A,2024-05-25 11:00:00,DELIVERED,29.99,"456 Maple Ave, Seattle, WA"
...
```

## Integration Test Class Template

Create `src/test/java/[package]/[TestName]IT.java`.

The test class supports both testcontainer and external modes via the base class helper methods. Tests use the `[AppName]App` and `CsvDataLoader` classes.

```java
package [package];

import org.junit.jupiter.api.Test;
import org.voltdb.VoltTable;
import org.voltdb.client.Client2;
import org.voltdb.types.TimestampType;
import org.voltdbtest.testcontainer.VoltDBCluster;

import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

public class [TestName]IT extends IntegrationTestBase {

    @Test
    public void test[Scenario]() {
        VoltDBCluster db = null;
        try {
            // ============================================
            // Setup: start VoltDB and deploy schema
            // ============================================
            Client2 client;
            if (isTestContainerMode()) {
                db = createTestContainer();
                startAndConfigureTestContainer(db);
                client = db.getClient2();
            } else {
                client = createExternalClient();
                configureExternalInstance(client);
            }

            [AppName]App app = new [AppName]App(client);
            CsvDataLoader loader = new CsvDataLoader();

            // ============================================
            // Load test data from CSV files
            // ============================================
            List<Long> primaryIds = loader.load[PrimaryTable]Data(app, "data/[primary_table].csv");
            List<Long> childIds = loader.load[ColocatedTable]Data(app, "data/[colocated_table].csv");

            assertEquals(5, primaryIds.size(), "All [primary entities] should be loaded");
            assertEquals(15, childIds.size(), "All [co-located entities] should be loaded");

            // ============================================
            // Verify single-partition: Get[PrimaryTable]
            // ============================================
            VoltTable table = app.get[PrimaryTable](1L);
            assertTrue(table.advanceRow(), "Should find [entity] 1");
            assertEquals("[expected_name]", table.getString("[name_column]"));

            // ============================================
            // Verify single-partition: Upsert[PrimaryTable] (update existing)
            // ============================================
            app.upsert[PrimaryTable](1L, "[updated_name]", ...);
            table = app.get[PrimaryTable](1L);
            assertTrue(table.advanceRow(), "Should find updated [entity]");
            assertEquals("[updated_name]", table.getString("[name_column]"));

            // ============================================
            // Verify single-partition: Get[ColocatedTable]By[PrimaryTable]
            // ============================================
            VoltTable childTable = app.get[ColocatedTable]By[PrimaryTable](1L);
            int childCount = 0;
            while (childTable.advanceRow()) {
                childCount++;
            }
            assertTrue(childCount > 0, "[Entity] 1 should have [children] from CSV");

            // ============================================
            // Verify single-partition: Upsert[ColocatedTable] (add new)
            // ============================================
            TimestampType now = new TimestampType(System.currentTimeMillis() * 1000);
            app.upsert[ColocatedTable](1L, 100L, ..., now, ...);
            childTable = app.get[ColocatedTable]By[PrimaryTable](1L);
            int newCount = 0;
            while (childTable.advanceRow()) {
                newCount++;
            }
            assertEquals(childCount + 1, newCount, "Should have one more [child] after upsert");

            // ============================================
            // Verify co-located access: Get[Primary]With[Related]
            // ============================================
            VoltTable[] results = app.get[Primary]With[Related](1L);
            assertEquals(2, results.length, "Should return 2 result tables");
            assertTrue(results[0].advanceRow(), "Should find the [primary entity]");
            int colocatedCount = 0;
            while (results[1].advanceRow()) {
                colocatedCount++;
            }
            assertEquals(newCount, colocatedCount,
                "Co-located query should return same count");

            // ============================================
            // Verify multi-partition: Search[Table]By[Field]
            // ============================================
            VoltTable searchResults = app.search[Table]By[Field]("[value]");
            int searchCount = 0;
            while (searchResults.advanceRow()) {
                searchCount++;
            }
            assertTrue(searchCount >= 1, "Should find matching records");

            // ============================================
            // Verify edge case: non-existent key
            // ============================================
            VoltTable emptyResult = app.get[PrimaryTable](999999L);
            assertFalse(emptyResult.advanceRow(),
                "Should return empty result for non-existent key");

            // ============================================
            // Cleanup
            // ============================================
            app.deleteAllData();

            // Verify cleanup
            VoltTable afterCleanup = app.get[PrimaryTable](1L);
            assertFalse(afterCleanup.advanceRow(), "No data should remain after cleanup");

            System.out.println("\n*** ALL TESTS PASSED ***\n");

        } catch (Exception e) {
            throw new RuntimeException(e);
        } finally {
            shutdownIfNeeded(db);
        }
    }
}
```

### Test Verification Patterns

- Load data via `CsvDataLoader`, assert expected counts (5 primary, 15 co-located)
- Query each type of operation through the app class methods (not raw procedure calls)
- For co-located procedures: verify multiple result tables returned
- For multi-partition searches: verify results match expected data
- Edge cases: non-existent keys return empty results — use `assertFalse`
- Cleanup: `deleteAllData()` + verify cleanup with another query

## test.properties Template

Create `src/test/resources/test.properties`:

```properties
# Docker image: "voltactivedata/volt-developer-edition" (default, free license)
# or "voltdb/voltdb-enterprise" (requires Enterprise license)
voltdb.image.name=voltactivedata/volt-developer-edition
voltdb.image.version=14.1.0_voltdb

# VoltDB test mode: "testcontainer" (default) or "external"
voltdb.test.mode=testcontainer

# External VoltDB connection settings (used when voltdb.test.mode=external)
voltdb.external.host=localhost
voltdb.external.port=21211

# Testcontainer shutdown behavior (used when voltdb.test.mode=testcontainer)
# Set to "false" to keep the container running after tests for debugging
voltdb.testcontainer.shutdown=true

# Project jar path — INCLUDE only if Java class procedures exist.
# OMIT this line when all procedures are DDL-defined.
project.jar.path=target/<project-name>-1.0.jar
```

**Notes:**
- `voltdb.image.name` and `voltdb.image.version` are hardcoded (no Maven filtering)
- Default image is Developer Edition (free license, no command logging). To use Enterprise Edition, change `voltdb.image.name` to `voltdb/voltdb-enterprise` and `voltdb.image.version` to `14.3.1`
- **Apple Silicon note:** The Developer Edition image is `amd64` only — it runs under Docker emulation on ARM Macs, which is slower
- `project.jar.path` must match the `<artifactId>` and `<version>` in pom.xml — omit when all procedures are DDL-defined
- Location is `src/test/resources/test.properties` (NOT `src/test/resources/integration/`)

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
# - Docker pulls Developer Edition image (first run only)
# - VoltDB container starts
# - JAR with stored procedures is loaded (only if Java class procedures exist)
# - DDL schema is applied from classpath (includes DDL-defined procedures)
# - CSV data is loaded via CsvDataLoader
# - All operations verified through app class methods
# - Container shuts down (unless voltdb.testcontainer.shutdown=false)
# - BUILD SUCCESS message

# TROUBLESHOOTING:
# "Cannot connect to Docker daemon" -> Start Docker: open -a Docker (macOS)
# "License file not found" -> Check VOLTDB_LICENSE env var or /tmp/voltdb-license.xml
# "DDL resource not found" -> Ensure ddl.sql is in src/main/resources/
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
# and use VoltDBSetup to deploy schema idempotently.
```

## Key Technical Details

| Item | Value |
|------|-------|
| Client API | `db.getClient2()` returns `Client2` |
| Procedure calls | Via `[AppName]App` methods (not raw `client.callProcedureAsync`) |
| Data loading | Via `CsvDataLoader` reading from classpath |
| CSV location | `src/main/resources/data/` |
| Test naming | `*IT.java` suffix (picked up by maven-failsafe-plugin) |
| test.properties | `src/test/resources/test.properties` (no filtering) |

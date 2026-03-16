# Maven Project Structure and Setup

> **Category:** Project Setup | **Impact:** MEDIUM

## Context

VoltDB client projects use Maven for build management. This rule defines the complete project structure, `pom.xml` template with all required dependencies and plugins, application class templates, and build/verify instructions.

## Prerequisites

Before creating a project, the skill MUST actively verify all prerequisites (see SKILL.md Step 1 and Step 2). Do not just document them — run the checks.

Required infrastructure:
- **Docker** — installed and running (checked silently in Step 1; user prompted only if not running)
- **Java 17+** — not checked upfront; missing/wrong version fails clearly at build time
- **Maven 3.6+** — not checked upfront; missing Maven fails clearly at build time
- **VoltDB Enterprise license** — file path confirmed by the user in Step 2

## Project Directory Structure

```
<project-name>/
├── pom.xml
├── README.md
├── src/
│   ├── main/
│   │   ├── java/<package>/
│   │   │   ├── [AppName]App.java
│   │   │   ├── VoltDBSetup.java
│   │   │   ├── CsvDataLoader.java
│   │   │   └── procedures/          ← only if Java class procedures exist
│   │   └── resources/
│   │       ├── ddl.sql
│   │       ├── remove_db.sql
│   │       └── data/
│   │           ├── [primary_table].csv
│   │           └── [colocated_table].csv
│   └── test/
│       ├── java/<package>/
│       │   ├── IntegrationTestBase.java
│       │   └── [TestName]IT.java
│       └── resources/
│           └── test.properties
```

**Note:** The `procedures/` directory and `volt-procedure-api` dependency are only needed when Java class procedures exist (co-located access or multi-step transactions). When all procedures are DDL-defined, omit them.

## pom.xml Template

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.example</groupId>
    <artifactId><project-name></artifactId>
    <version>1.0</version>
    <packaging>jar</packaging>

    <properties>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <maven.compiler.source>17</maven.compiler.source>
        <maven.compiler.target>17</maven.compiler.target>
        <voltdb.version>14.3.1</voltdb.version>
        <volt-procedure-api.version>15.0.0</volt-procedure-api.version>
        <volt-testcontainer.version>1.7.0</volt-testcontainer.version>
    </properties>

    <dependencies>
        <!-- VoltDB Procedure API (for Java class stored procedures) - provided scope since
             procedures run on the VoltDB server, not in the client application.
             Note: volt-procedure-api uses a different version from voltdbclient.
             OMIT this dependency if all procedures are DDL-defined (no Java class procedures). -->
        <dependency>
            <groupId>org.voltdb</groupId>
            <artifactId>volt-procedure-api</artifactId>
            <version>${volt-procedure-api.version}</version>
            <scope>provided</scope>
        </dependency>
        <dependency>
            <groupId>org.voltdb</groupId>
            <artifactId>voltdbclient</artifactId>
            <version>${voltdb.version}</version>
        </dependency>

        <!-- SLF4J (required by voltdbclient at runtime) -->
        <dependency>
            <groupId>org.slf4j</groupId>
            <artifactId>slf4j-api</artifactId>
            <version>2.0.9</version>
        </dependency>
        <dependency>
            <groupId>org.slf4j</groupId>
            <artifactId>slf4j-simple</artifactId>
            <version>2.0.9</version>
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
                <configuration>
                    <archive>
                        <manifest>
                            <mainClass>[package].[AppName]App</mainClass>
                        </manifest>
                    </archive>
                </configuration>
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

## VoltDBSetup.java Template

Create `src/main/java/[package]/VoltDBSetup.java`:

```java
package [package];

import org.voltdb.client.Client2;
import org.voltdb.client.ClientResponse;
import org.voltdb.VoltTable;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;

/**
 * One-time schema deployment utility.
 * Checks whether schema is already deployed via @SystemCatalog.
 * If not, loads procedure classes (if any) and executes DDL.
 *
 * When all procedures are DDL-defined: omit JAR_PATH, @UpdateClasses block,
 * and the java.io.File / java.nio.file.Files imports.
 */
public class VoltDBSetup {

    // Include JAR_PATH only if the project has Java class procedures.
    // Omit this field and the @UpdateClasses block below when all procedures are DDL-defined.
    private static final String JAR_PATH = "target/<project-name>-1.0.jar";
    private static final String DDL_RESOURCE = "ddl.sql";

    private final Client2 client;

    public VoltDBSetup(Client2 client) {
        this.client = client;
    }

    /**
     * Deploy stored procedure classes (if any) and DDL schema to VoltDB,
     * but only if the schema has not already been deployed.
     * Uses @SystemCatalog TABLES to check for the primary table.
     */
    public void initSchemaIfNeeded() throws Exception {
        if (isSchemaDeployed()) {
            System.out.println("Schema already deployed — skipping.");
            return;
        }

        // --- @UpdateClasses block: INCLUDE only if Java class procedures exist ---
        // --- OMIT this entire block when all procedures are DDL-defined ---
        File jarFile = new File(JAR_PATH);
        if (!jarFile.exists()) {
            throw new RuntimeException(
                "Jar not found: " + JAR_PATH + ". Run 'mvn package -DskipTests' first.");
        }

        // Load procedure classes
        System.out.println("Loading classes from: " + jarFile);
        byte[] jarBytes = Files.readAllBytes(jarFile.toPath());
        ClientResponse response = client.callProcedureSync("@UpdateClasses", jarBytes, null);
        if (response.getStatus() != ClientResponse.SUCCESS) {
            throw new RuntimeException("Failed to load classes: " + response.getStatusString());
        }
        System.out.println("Classes loaded successfully.");
        // --- End @UpdateClasses block ---

        // Execute DDL
        String ddl = loadResourceAsString(DDL_RESOURCE);
        if (ddl == null) {
            throw new RuntimeException("DDL resource not found: " + DDL_RESOURCE);
        }
        System.out.println("Loading schema from classpath: " + DDL_RESOURCE);
        ClientResponse ddlResponse = client.callProcedureSync("@AdHoc", ddl);
        if (ddlResponse.getStatus() != ClientResponse.SUCCESS) {
            throw new RuntimeException("DDL failed: " + ddlResponse.getStatusString());
        }
        System.out.println("Schema deployment complete.");
    }

    private boolean isSchemaDeployed() throws Exception {
        ClientResponse response = client.callProcedureSync("@SystemCatalog", "TABLES");
        VoltTable tables = response.getResults()[0];
        while (tables.advanceRow()) {
            String tableName = tables.getString("TABLE_NAME");
            if ("[PRIMARY_TABLE]".equalsIgnoreCase(tableName)) {
                return true;
            }
        }
        return false;
    }

    private String loadResourceAsString(String resourcePath) {
        try (InputStream is = getClass().getClassLoader().getResourceAsStream(resourcePath)) {
            if (is == null) {
                System.err.println("Resource not found: " + resourcePath);
                return null;
            }
            return new String(is.readAllBytes(), StandardCharsets.UTF_8);
        } catch (IOException e) {
            throw new RuntimeException("Failed to read resource: " + resourcePath, e);
        }
    }
}
```

**Customization notes:**
- Replace `[PRIMARY_TABLE]` in `isSchemaDeployed()` with the actual primary table name
- Replace `<project-name>` in `JAR_PATH` with the actual project artifactId
- **When all procedures are DDL-defined:** remove `JAR_PATH`, the `@UpdateClasses` block, and the `java.io.File` / `java.nio.file.Files` imports. The method only needs to execute DDL via `@AdHoc`.

## [AppName]App.java Template

Create `src/main/java/[package]/[AppName]App.java`:

```java
package [package];

import org.voltdb.VoltTable;
import org.voltdb.client.Client2;
import org.voltdb.client.Client2Config;
import org.voltdb.client.ClientFactory;
import org.voltdb.client.ClientResponse;
import org.voltdb.types.TimestampType;

import java.util.List;

/**
 * [AppName] VoltDB client application.
 * Demonstrates CRUD and search operations using VoltDB stored procedures.
 * All operations use callProcedureAsync() internally for non-blocking execution.
 */
public class [AppName]App {

    private final Client2 client;

    public [AppName]App(Client2 client) {
        this.client = client;
    }

    // ========================================
    // CRUD Operations
    // ========================================

    // Generate one method per stored procedure.
    // Each method calls client.callProcedureAsync(), validates via checkResponse(), and blocks with .get().
    //
    // Single-partition upsert example:
    // public void upsert[Table](long partitionKey, ...) throws Exception {
    //     client.callProcedureAsync("Upsert[Table]", partitionKey, ...)
    //         .thenApply(response -> checkResponse("Upsert[Table]", response))
    //         .get();
    // }
    //
    // Single-partition get example (returns VoltTable):
    // public VoltTable get[Table](long partitionKey) throws Exception {
    //     return client.callProcedureAsync("Get[Table]", partitionKey)
    //         .thenApply(response -> checkResponse("Get[Table]", response).getResults()[0])
    //         .get();
    // }
    //
    // Co-located access example (returns VoltTable[]):
    // public VoltTable[] get[Table]With[Related](long partitionKey) throws Exception {
    //     return client.callProcedureAsync("Get[Table]With[Related]", partitionKey)
    //         .thenApply(response -> checkResponse("Get[Table]With[Related]", response).getResults())
    //         .get();
    // }

    // ========================================
    // Search Operations (multi-partition)
    // ========================================

    // public VoltTable search[Table]By[Field](String value) throws Exception {
    //     return client.callProcedureAsync("Search[Table]By[Field]", value)
    //         .thenApply(response -> checkResponse("Search[Table]By[Field]", response).getResults()[0])
    //         .get();
    // }

    // ========================================
    // Cleanup
    // ========================================

    public void deleteAllData() throws Exception {
        // Delete in child-first order (reverse of creation), chained with thenCompose
        client.callProcedureAsync("@AdHoc", "DELETE FROM [CHILD_TABLE];")
            .thenCompose(r -> client.callProcedureAsync("@AdHoc", "DELETE FROM [PRIMARY_TABLE];"))
            .get();
        System.out.println("All data deleted.");
    }

    // ========================================
    // Internal
    // ========================================

    private static ClientResponse checkResponse(String procName, ClientResponse response) {
        if (response.getStatus() != ClientResponse.SUCCESS) {
            throw new RuntimeException(procName + " failed: " + response.getStatusString());
        }
        return response;
    }

    // ========================================
    // Utility
    // ========================================

    public static void printTable(String label, VoltTable table) {
        System.out.println("\n--- " + label + " ---");
        System.out.println(table.toFormattedString());
    }

    // ========================================
    // Main entry point
    // ========================================

    public static void main(String[] args) throws Exception {
        String host = args.length > 0 ? args[0] : "localhost";
        int port = args.length > 1 ? Integer.parseInt(args[1]) : 21211;

        Client2Config config = new Client2Config();
        Client2 client = ClientFactory.createClient(config);
        client.connectSync(host, port);
        System.out.println("Connected to VoltDB at " + host + ":" + port);

        try {
            // One-time schema setup — skip if tables and procedures are already loaded
            new VoltDBSetup(client).initSchemaIfNeeded();

            [AppName]App app = new [AppName]App(client);
            CsvDataLoader loader = new CsvDataLoader();

            app.deleteAllData();

            // Load sample data from CSV files
            loader.load[PrimaryTable]Data(app, "data/[primary_table].csv");
            loader.load[ChildTable]Data(app, "data/[child_table].csv");

            // --- Demonstrate each type of operation the app supports ---
            // Generate one simple call per operation type, with sample arguments,
            // and print the result. Apps may have any combination of these.
            //
            // Order calls to reflect data dependencies of the specific app.
            // Typically: insert/upsert reference data first, then exercise the
            // core transaction, then query the results.
            //
            // Example ordering for an app with CRUD + multi-step transaction:
            //   1. app.upsert[RefTable](...);    // insert data the transaction depends on
            //   2. VoltTable result = app.coreTransaction(...);  // the main operation
            //      result.advanceRow();
            //      System.out.printf("Result: %s%n", result.getString("STATUS"));
            //   3. printTable("Details", app.get[Table](...));   // single-partition read
            //   4. printTable("Search", app.search[Table]By[Field]("value")); // multi-partition
            //
            // For CRUD-only apps (no multi-step transaction):
            //   1. app.upsert[Table](...);
            //   2. printTable("Get [Entity]", app.get[Table](...));
            //   3. printTable("Search", app.search[Table]By[Field]("value"));

            app.deleteAllData();

        } finally {
            client.close();
        }
    }
}
```

**Customization notes:**
- Replace `[AppName]` with the application name (e.g., `WildlifeRehab`)
- Generate real (not commented-out) code for all method bodies and the `main()` body
- The `deleteAllData()` method must delete in child-first order
- **CRITICAL: `main()` must demonstrate all operation types the app supports** — one simple call per type (CRUD, multi-step transaction, co-located access, multi-partition search). Order calls to reflect data dependencies: insert/upsert reference data that the transaction needs first, then call the core transaction, then query results. Keep each demonstration simple: one call with sample arguments, print the result.

## Key Technical Details

| Item | Value |
|------|-------|
| VoltDBCluster import | `org.voltdbtest.testcontainer.VoltDBCluster` |
| Docker image | `voltdb/voltdb-enterprise:` + version |
| DDL location | `src/main/resources/ddl.sql` (classpath resource) |
| remove_db.sql | `src/main/resources/remove_db.sql` (classpath resource) |
| Procedure dependency | `volt-procedure-api` (NOT `voltdb`) — only if Java class procedures exist |
| Constructor | `new VoltDBCluster(licensePath, image, extraLibDir)` |

## Build and Verify Instructions

```bash
# 1. VERIFY DOCKER IS RUNNING (tests require Docker)
docker info
# If not running: macOS: open -a Docker | Linux: sudo systemctl start docker

# 2. SET UP VOLTDB LICENSE (if not already done)
export VOLTDB_LICENSE=/path/to/voltdb-license.xml
# OR: cp /path/to/voltdb-license.xml /tmp/voltdb-license.xml

# 3. NAVIGATE TO PROJECT DIRECTORY
cd <project-name>

# 4. BUILD THE PROJECT (compile and package without running tests)
mvn clean package -DskipTests

# 5. RUN INTEGRATION TESTS (starts VoltDB in Docker, loads schema, runs tests)
mvn verify

# EXPECTED OUTPUT ON SUCCESS:
# - Docker pulls voltdb/voltdb-enterprise image (first run only)
# - VoltDB container starts
# - JAR with stored procedures is loaded (only if Java class procedures exist)
# - DDL schema is applied from classpath (includes DDL-defined procedures)
# - CSV data is loaded via CsvDataLoader
# - All query scenarios verified
# - Container shuts down
# - BUILD SUCCESS message

# TROUBLESHOOTING:
# "Cannot connect to Docker daemon" -> Start Docker: open -a Docker (macOS)
# "License file not found" -> Check VOLTDB_LICENSE env var or /tmp/voltdb-license.xml
# "DDL resource not found" -> Ensure ddl.sql is in src/main/resources/
# "Connection refused" -> Wait for Docker to fully start, then retry
```

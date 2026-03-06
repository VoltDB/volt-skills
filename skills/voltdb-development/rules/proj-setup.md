# Maven Project Structure and Setup

> **Category:** Project Setup | **Impact:** MEDIUM

## Context

VoltDB client projects use Maven for build management. This rule defines the complete project structure, `pom.xml` template with all required dependencies and plugins, application class templates, and build/verify instructions.

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
├── README.md
├── src/
│   ├── main/
│   │   ├── java/<package>/
│   │   │   ├── [AppName]App.java
│   │   │   ├── VoltDBSetup.java
│   │   │   ├── CsvDataLoader.java
│   │   │   └── procedures/
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
        <!-- VoltDB Procedure API (for stored procedures) - provided scope since
             procedures run on the VoltDB server, not in the client application.
             Note: volt-procedure-api uses a different version from voltdbclient. -->
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
 * If not, loads procedure classes and executes DDL.
 */
public class VoltDBSetup {

    private static final String JAR_PATH = "target/<project-name>-1.0.jar";
    private static final String DDL_RESOURCE = "ddl.sql";

    private final Client2 client;

    public VoltDBSetup(Client2 client) {
        this.client = client;
    }

    /**
     * Deploy stored procedure classes and DDL schema to VoltDB,
     * but only if the schema has not already been deployed.
     * Uses @SystemCatalog TABLES to check for the primary table.
     */
    public void initSchemaIfNeeded() throws Exception {
        if (isSchemaDeployed()) {
            System.out.println("Schema already deployed — skipping.");
            return;
        }

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

        // Execute DDL
        String ddl = loadResourceAsString(DDL_RESOURCE);
        if (ddl == null) {
            throw new RuntimeException("DDL resource not found: " + DDL_RESOURCE);
        }
        System.out.println("Loading schema from classpath: " + DDL_RESOURCE);
        response = client.callProcedureSync("@AdHoc", ddl);
        if (response.getStatus() != ClientResponse.SUCCESS) {
            throw new RuntimeException("DDL failed: " + response.getStatusString());
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

            // Cleanup tables if you want to remove old state
            app.deleteAllData();

            // Load sample data from CSV files
            // List<Long> primaryIds = loader.load[PrimaryTable]Data(app, "data/[primary_table].csv");
            // List<Long> childIds = loader.load[ChildTable]Data(app, "data/[child_table].csv");

            // Exercise single-partition reads
            // printTable("Get [Entity] 1", app.get[Table](1L));

            // Exercise co-located access
            // VoltTable[] results = app.get[Table]With[Related](1L);
            // printTable("[Table] (co-located)", results[0]);
            // printTable("[Related] (co-located)", results[1]);

            // Exercise multi-partition searches
            // printTable("Search by [field]", app.search[Table]By[Field]("value"));

            // Cleanup
            app.deleteAllData();

        } finally {
            client.close();
        }
    }
}
```

**Customization notes:**
- Replace `[AppName]` with the application name (e.g., `WildlifeRehab`)
- Uncomment and adapt method signatures based on the generated stored procedures
- The `deleteAllData()` method must delete in child-first order
- `main()` exercises all major operations as a demonstration

## Key Technical Details

| Item | Value |
|------|-------|
| VoltDBCluster import | `org.voltdbtest.testcontainer.VoltDBCluster` |
| Docker image | `voltdb/voltdb-enterprise:` + version |
| DDL location | `src/main/resources/ddl.sql` (classpath resource) |
| remove_db.sql | `src/main/resources/remove_db.sql` (classpath resource) |
| Procedure dependency | `volt-procedure-api` (NOT `voltdb`) |
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
# - JAR with stored procedures is loaded
# - DDL schema is applied from classpath
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

---
name: voltdb-client-helper
description: Helps create VoltDB client applications with connection code, DDL schemas, stored procedures, and integration tests. Use when user wants to create a VoltDB client, connect to VoltDB, create VoltDB schemas, or write VoltDB stored procedures.
---

# VoltDB Client Helper

This skill helps you create VoltDB client applications based on the [volt-testcontainer](https://github.com/VoltDB/volt-testcontainer) project patterns.

## Capabilities

- Create Java client code
- Generate DDL schemas
- Create stored procedures
- Generate test data generators for DDL schemas
- Generate integration tests using VoltDBCluster
- Provide run instructions

## Prerequisites

Before using this skill, ensure:
- **Docker** is installed and running (required for VoltDB testcontainer)
- **Java 17+** is installed
- **Maven 3.6+** is installed
- **VoltDB Enterprise license** file is available

### Verify Prerequisites

```bash
# 1. Verify Docker is running (REQUIRED - tests will fail without Docker)
docker info

# If Docker is not running, start it:
# macOS: open -a Docker
# Linux: sudo systemctl start docker

# 2. Verify Java version
java -version

# 3. Verify Maven version
mvn -version

# 4. Set up VoltDB license (choose one option)
# Option A: Environment variable (recommended)
export VOLTDB_LICENSE=/path/to/your/license.xml

# Option B: Copy to default location
cp /path/to/your/license.xml /tmp/voltdb-license.xml
```

## Instructions

When invoked, follow this workflow:

### Step 1: Gather Requirements

Ask the user:
1. **Project name**: What should the project be called?
2. **Package name**: Java package (default: com.example.voltdb)
3. **Schema preference**:
   - Use default KEYVALUE schema
   - Describe custom tables
4. **Stored procedures**:
   - Use default Put/Get procedures
   - Describe custom operations
5. **Output directory**: Where to create the project?

### Step 2: Create Project Structure

```
<project-name>/
├── pom.xml
├── schema/
│   └── ddl.sql
├── src/
│   ├── main/java/<package>/
│   │   └── procedures/
│   │       ├── Put.java
│   │       └── Get.java
│   └── test/
│       ├── java/<package>/
│       │   ├── IntegrationTestBase.java
│       │   ├── TestDataGenerator.java
│       │   └── KeyValueIT.java
│       └── resources/integration/
│           └── test.properties
└── README.md
```

### Step 3: Generate pom.xml

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
        <volt-testcontainer.version>1.6.0</volt-testcontainer.version>
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

### Step 4: Generate DDL Schema

**IMPORTANT:** Schema file is at `schema/ddl.sql` (NOT in resources)

```sql
-- VoltDB DDL Schema
file -inlinebatch END_OF_BATCH

CREATE TABLE KEYVALUE
(
    KEYNAME integer NOT NULL,
    VALUE varchar(5000) NOT NULL
);

PARTITION TABLE KEYVALUE ON COLUMN KEYNAME;

CREATE PROCEDURE FROM CLASS <package>.Put;
CREATE PROCEDURE FROM CLASS <package>.Get;

END_OF_BATCH
```

### Step 5: Generate Stored Procedures

**Put.java:**
```java
package <package>;

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

**Get.java:**
```java
package <package>;

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

### Step 6: Generate Integration Test Base

**IntegrationTestBase.java:**
```java
package <package>;

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

### Step 7: Generate Test Data Generator

**TestDataGenerator.java:**
```java
package <package>;

import org.voltdb.client.Client;
import org.voltdb.client.ClientResponse;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

/**
 * Generates test data for the KEYVALUE table.
 * Customize this class to generate data for your specific schema.
 */
public class TestDataGenerator {

    private final Client client;
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

    public TestDataGenerator(Client client) {
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

            ClientResponse response = client.callProcedure("Put", key, value);
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
            ClientResponse response = client.callProcedure("Get", key);
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

### Step 8: Generate Integration Test

**KeyValueIT.java:**
```java
package <package>;

import org.junit.jupiter.api.Test;
import org.voltdb.client.Client;
import org.voltdb.client.ClientResponse;
import org.voltdb.VoltTable;
import org.voltdbtest.testcontainer.VoltDBCluster;

import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

public class KeyValueIT extends IntegrationTestBase {

    private static final int TEST_DATA_COUNT = 10;

    @Test
    public void testKeyValue() {
        VoltDBCluster db = new VoltDBCluster(
            getLicensePath(),
            "voltdb/voltdb-enterprise:" + getImageVersion(),
            getExtraLibDirectory()
        );
        try {
            configureTestContainer(db);
            Client client = db.getClient();

            // Use TestDataGenerator to insert test data
            TestDataGenerator generator = new TestDataGenerator(client);
            List<Integer> insertedKeys = generator.generateTestData(TEST_DATA_COUNT);

            // Verify data was inserted
            assertEquals(TEST_DATA_COUNT, insertedKeys.size(),
                "All test records should be inserted");

            // Query and print all inserted data
            generator.queryAndPrintData(insertedKeys);

            // Verify individual record retrieval
            int testKey = insertedKeys.get(0);
            ClientResponse response = client.callProcedure("Get", testKey);
            assertEquals(ClientResponse.SUCCESS, response.getStatus());

            VoltTable table = response.getResults()[0];
            assertTrue(table.advanceRow(), "Should have a result row");
            String value = table.getString(0);
            System.out.printf("%nVerification: key=%d retrieved value='%s'%n", testKey, value);

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

### Step 9: Generate test.properties

Create `src/test/resources/integration/test.properties`:
```properties
voltdb.image.version=${voltdb.version}
```

### Step 10: Generate README

Include:
1. Prerequisites (Java 17+, Maven 3.6+, Docker, VoltDB license)
2. License setup instructions
3. Build: `mvn clean package`
4. Run tests: `mvn verify`
5. VoltDBCluster usage pattern

### Step 11: Provide Build and Verify Instructions

After generating the project, provide these instructions to the user:

```bash
# ============================================
# BUILD AND VERIFY THE GENERATED PROJECT
# ============================================

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

# ============================================
# EXPECTED OUTPUT ON SUCCESS
# ============================================
# - Docker pulls voltdb/voltdb-enterprise image (first run only)
# - VoltDB container starts
# - JAR with stored procedures is loaded
# - DDL schema is applied
# - Test data generator inserts 10 sample records
# - Test data generator queries and prints all records
# - Verification test passes
# - Container shuts down
# - BUILD SUCCESS message

# ============================================
# TROUBLESHOOTING
# ============================================
# "Cannot connect to Docker daemon" → Start Docker: open -a Docker (macOS)
# "License file not found" → Check VOLTDB_LICENSE env var or /tmp/voltdb-license.xml
# "Schema file not found" → Ensure schema/ddl.sql exists in project root
# "Connection refused" → Wait for Docker to fully start, then retry
```

## Key Technical Details

| Item | Value |
|------|-------|
| VoltDBCluster import | `org.voltdbtest.testcontainer.VoltDBCluster` |
| Docker image | `voltdb/voltdb-enterprise:` + version |
| Schema location | `schema/ddl.sql` (NOT in resources) |
| Procedure dependency | `volt-procedure-api` (NOT `voltdb`) |
| Constructor | `new VoltDBCluster(licensePath, image, extraLibDir)` |

## Error Handling

- Validate package names follow Java conventions
- Check schema file exists before running DDL
- Provide clear license setup instructions

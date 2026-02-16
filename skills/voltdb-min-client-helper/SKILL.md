---
name: voltdb-min-client-helper
description: Creates minimal VoltDB client Maven projects with connection code, dependencies, and build configuration. Use when user wants to create a new VoltDB project, set up Maven dependencies, or scaffold a VoltDB client application.
---

# VoltDB Minimal Client Helper

This skill creates a minimal, buildable VoltDB client Maven project. It provides the project scaffolding that other skills (`voltdb-proc-helper`, `voltdb-it-tests-helper`) populate with schema-specific content.

For a complete end-to-end experience with partitioning analysis, use `voltdb-partitioned-client-helper` instead.

## Capabilities

- Create Maven project scaffolding with VoltDB dependencies
- Generate `pom.xml` with correct plugin configuration
- Provide build and verify instructions
- Optionally generate a simple Key-Value example (DDL, procedures, tests) as a quick-start

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
3. **Output directory**: Where to create the project?
4. **Quick-start example**: Include a simple Key-Value example? (If yes, also use `voltdb-proc-helper` and `voltdb-it-tests-helper` to generate the example DDL, procedures, and tests)

### Step 2: Create Project Structure

```
<project-name>/
├── pom.xml
├── schema/
│   └── ddl.sql
├── src/
│   ├── main/java/<package>/
│   │   └── procedures/
│   └── test/
│       ├── java/<package>/
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
        <volt-testcontainer.version>1.6.0-SNAPSHOT</volt-testcontainer.version>
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

### Step 4: Generate README

Include:
1. Project description
2. Prerequisites (Java 17+, Maven 3.6+, Docker, VoltDB license)
3. License setup instructions
4. Build: `mvn clean package -DskipTests`
5. Run tests: `mvn verify`

### Step 5: Provide Build and Verify Instructions

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
# - Test data is generated and verified
# - Container shuts down
# - BUILD SUCCESS message

# ============================================
# TROUBLESHOOTING
# ============================================
# "Cannot connect to Docker daemon" -> Start Docker: open -a Docker (macOS)
# "License file not found" -> Check VOLTDB_LICENSE env var or /tmp/voltdb-license.xml
# "Schema file not found" -> Ensure schema/ddl.sql exists in project root
# "Connection refused" -> Wait for Docker to fully start, then retry
```

## Key Technical Details

| Item | Value |
|------|-------|
| VoltDBCluster import | `org.voltdbtest.testcontainer.VoltDBCluster` |
| Docker image | `voltdb/voltdb-enterprise:` + version |
| Schema location | `schema/ddl.sql` (NOT in resources) |
| Procedure dependency | `volt-procedure-api` (NOT `voltdb`) |
| Constructor | `new VoltDBCluster(licensePath, image, extraLibDir)` |

## Related Skills

| Skill | Use For |
|-------|---------|
| `voltdb-proc-helper` | Generate DDL schemas and stored procedures |
| `voltdb-it-tests-helper` | Generate integration tests with testcontainer |
| `voltdb-partitioned-client-helper` | Full end-to-end guided experience with partitioning |

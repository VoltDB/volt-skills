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

    // ========================================
    // Configuration
    // ========================================

    public String getImageVersion() {
        return props.getProperty("voltdb.image.version", "14.3.1");
    }

    public String getTestMode() {
        return props.getProperty("voltdb.test.mode", "testcontainer");
    }

    public boolean isTestContainerMode() {
        return "testcontainer".equalsIgnoreCase(getTestMode());
    }

    public boolean isShutdownOnCompletion() {
        return Boolean.parseBoolean(
            props.getProperty("voltdb.testcontainer.shutdown", "true"));
    }

    public String getExternalHost() {
        return props.getProperty("voltdb.external.host", "localhost");
    }

    public int getExternalPort() {
        return Integer.parseInt(
            props.getProperty("voltdb.external.port", "21211"));
    }

    // ========================================
    // Testcontainer lifecycle
    // ========================================

    public VoltDBCluster createTestContainer() {
        return new VoltDBCluster(
            getLicensePath(),
            "voltdb/voltdb-enterprise:" + getImageVersion(),
            getExtraLibDirectory()
        );
    }

    public void startAndConfigureTestContainer(VoltDBCluster db) {
        try {
            db.start();
            File jar = getProjectJar();
            if (jar != null) {
                System.out.println("Loading classes from: " + jar);
                ClientResponse response = db.loadClasses(jar.getAbsolutePath());
                assertEquals(ClientResponse.SUCCESS, response.getStatus(),
                    "Load classes must pass");
            }

            File schemaFile = extractResourceToTempFile("ddl.sql");
            if (schemaFile != null) {
                System.out.println("Loading schema from classpath resource: ddl.sql");
                assertTrue(db.runDDL(schemaFile), "Schema must get loaded");
            } else {
                System.err.println("Schema resource not found: ddl.sql");
            }
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    public Client2 createExternalClient() throws Exception {
        Client2Config config = new Client2Config();
        Client2 client = ClientFactory.createClient(config);
        String host = getExternalHost();
        int port = getExternalPort();
        System.out.println("Connecting to external VoltDB at " + host + ":" + port);
        client.connectSync(host, port);
        return client;
    }

    public void configureExternalInstance(Client2 client) {
        try {
            new VoltDBSetup(client).initSchemaIfNeeded();
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    public void shutdownIfNeeded(VoltDBCluster db) {
        if (db != null && isShutdownOnCompletion()) {
            System.out.println("Shutting down VoltDB testcontainer...");
            db.shutdown();
        } else if (db != null) {
            System.out.println("Keeping VoltDB testcontainer running (shutdown disabled).");
        }
    }

    // ========================================
    // Internal helpers
    // ========================================

    protected File extractResourceToTempFile(String resourcePath) {
        try (InputStream is = getClass().getClassLoader().getResourceAsStream(resourcePath)) {
            if (is == null) return null;
            File tempFile = File.createTempFile("voltdb-", ".sql");
            tempFile.deleteOnExit();
            Files.copy(is, tempFile.toPath(), java.nio.file.StandardCopyOption.REPLACE_EXISTING);
            return tempFile;
        } catch (IOException e) {
            throw new RuntimeException("Failed to extract resource: " + resourcePath, e);
        }
    }

    protected String getExtraLibDirectory() {
        File libdir = new File("target/lib");
        if (libdir.exists() && libdir.isDirectory() &&
            Arrays.stream(libdir.listFiles())
                .anyMatch(file -> file.getName().toLowerCase().endsWith(".jar"))) {
            return libdir.getAbsolutePath();
        }
        return null;
    }

    protected File getProjectJar() {
        String jarPath = props.getProperty("project.jar.path");
        if (jarPath != null) {
            File jar = new File(jarPath);
            if (jar.exists()) {
                return jar;
            }
        }
        return null;
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

## Key Details

| Item | Value |
|------|-------|
| VoltDBCluster import | `org.voltdbtest.testcontainer.VoltDBCluster` |
| Client API | `db.getClient2()` returns `Client2` |
| Test mode property | `voltdb.test.mode` = `testcontainer` or `external` |
| Shutdown property | `voltdb.testcontainer.shutdown` = `true` or `false` |
| Schema loading | `extractResourceToTempFile("ddl.sql")` — loads DDL from classpath |
| External mode | Delegates to `VoltDBSetup.initSchemaIfNeeded()` |
| Project JAR | Read from `project.jar.path` in test.properties |

## Important Differences from Old Pattern

- **Schema loaded from classpath** — uses `extractResourceToTempFile()` instead of filesystem `File`
- **Method name:** `startAndConfigureTestContainer()` (not `configureTestContainer()`)
- **External mode:** delegates to `VoltDBSetup` instead of inline `@UpdateClasses`/`@AdHoc`
- **No CSV logic** — CSV loading is handled by `CsvDataLoader` in the test class
- **Compact `getLicensePath()`** — no verbose error messages, falls back silently
- **`getProjectJar()`** — reads jar path from test.properties `project.jar.path`

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

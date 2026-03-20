# Testing (pipelines + plugins)

Use this to pick the right test level, set up VoltSP Testcontainers, and write integration tests.
For concrete implementation shapes derived from E2E tests, read `references/pipeline-kinds.md`.

## Choose the test level

- Use unit tests for pure logic and mapping functions.
- Use in-process simulation (if available) for pipeline behavior without container overhead.
- Use Testcontainers for integration boundaries (Kafka, Schema Registry, VoltDB, real VoltSP image).
- Use black-box container tests before release when runtime wiring matters (classpath, config files, license, worker count).

## Maven dependencies for testing

Add to `pom.xml` with `test` scope:

```xml
<dependency>
    <groupId>org.voltdb</groupId>
    <artifactId>volt-stream-testcontainer</artifactId>
    <version>1.7.1</version>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>org.voltdb</groupId>
    <artifactId>volt-stream-api-test</artifactId>
    <version>1.7.1</version>
    <scope>test</scope>
</dependency>
```

`volt-stream-testcontainer` provides `VoltSpContainer` and path helpers.
`volt-stream-api-test` provides `ResourceHelper` for locating license files and keystores.

Also include JUnit 5, AssertJ, and a Log4j2 SLF4J binding (for container log output). The template POM at `assets/templates/maven/pom.xml` already includes all of these.

## Prerequisites

- Docker daemon running (Testcontainers launches containers via Docker).
- VoltDB license file at `~/license.xml` or `/tmp/license.xml` (searched automatically by `ResourceHelper.getVoltLicenseLocation()`).

## VoltSpContainer API

`VoltSpContainer` extends Testcontainers `GenericContainer<VoltSpContainer>`. It launches a dockerized VoltSP instance with your pipeline, configuration, and classpath mounted into the container.

Docker image: `voltdb/volt-streams` (default tag: `master--latest`).

### Factory methods

```java
VoltSpContainer.newVoltSp()                        // default tag
VoltSpContainer.newVoltSp("1.7.1")                 // specific tag
VoltSpContainer.newVoltSp(DockerImageName.parse("voltdb/volt-streams-dev").withTag("1.7.1"))
```

### Builder methods (all return `this` for chaining)

| Method | Purpose |
|---|---|
| `withParallelism(int)` | Number of worker threads (default: 1) |
| `withPipelineClass(Class<?>)` | Java DSL pipeline to run |
| `withPipelineDefinitionYaml(Path)` | YAML pipeline definition file |
| `withPipelineDefinitionYaml(String, Object...)` | Inline YAML with `String.format` args |
| `withConfigurationYaml(Path)` | Runtime configuration file |
| `withConfigurationYaml(String, Object...)` | Inline configuration YAML with `String.format` args |
| `withVoltLicense(Path)` or `withVoltLicense(String)` | **Required.** Path to VoltDB license file |
| `withClassesUnder(MountPath)` | Mount compiled classes into container |
| `withAppJar(Path)` | Mount a fat JAR instead of classes |
| `with3rdPartyJar(groupId, artifactId, version)` | Add a dependency JAR from the classpath |
| `withNetwork(String alias, Network network)` | Join a Testcontainers network with alias |
| `withExposedPorts(int...)` | Expose additional container ports |
| `withEnv(String key, String value)` | Set environment variable (inherited from GenericContainer) |
| `withLogger(Logger)` | Pipe container output to SLF4J logger |
| `withLoggerName(String)` | Create and attach a named logger |
| `withDebugLogging()` | Enable debug-level output |
| `withDebugger(int port, boolean suspend)` | Attach remote Java debugger |
| `withDebugger(boolean suspend)` | Debugger on default port 8000 |

### Startup methods

```java
container.awaitStart(Duration.ofSeconds(30))   // waits for GET /metrics → 200
container.awaitStart(WaitStrategy)              // custom wait strategy
container.startAdGet()                          // start without health-check wait
```

### Runtime methods

```java
container.getLogs()                  // all stdout/stderr output so far
container.getMetricsPort()           // mapped metrics port (internal 11781)
container.getMetricsAddress()        // HostAndPort for metrics
container.getAddress(int port)       // HostAndPort for any exposed port
container.getMappedPort(int port)    // mapped port number
container.isRunning()                // container status
container.shutdown()                 // graceful stop
```

### Validation rules

The container validates on start:
1. Exactly one of `pipelineClass` or `pipelineDefinitionYaml` must be set (not both, not neither).
2. `voltLicensePath` is required.
3. At least one of `appJarPath`, `pipelineDefinitionYamlPath`, or `mountableClasses` must be set.

## Path helpers

### MavenPaths

Locates Maven build output directories. Requires prior `mvn compile` / `mvn test-compile`.

```java
MavenPaths.mavenClasses()                      // target/classes (all)
MavenPaths.mavenClasses("com.example.app")     // target/classes filtered to package
MavenPaths.mavenTestClasses()                  // target/test-classes (all)
MavenPaths.mavenTestClasses("com.example.app") // target/test-classes filtered to package
MavenPaths.mavenTestResource("config.yaml")    // resolve file under target/test-classes
```

### WorkingDirPaths

Resolves paths relative to the project root (useful for data files outside `target/`).

```java
WorkingDirPaths.resolve("data/models")         // project-root/data/models as MountPath
WorkingDirPaths.resolve(Path.of("data/models"))
```

### ResourceHelper (from volt-stream-api-test)

```java
ResourceHelper.getVoltLicenseLocation()  // searches ~/license.xml then /tmp/license.xml
```

## Black-box test pattern (Java DSL pipeline)

Minimal test that launches a Java pipeline in a container and verifies output:

```java
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.VoltSpContainer;
import org.testcontainers.containers.path.MavenPaths;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;
import org.voltsp.test.container.ResourceHelper;

import java.time.Duration;

import static org.assertj.core.api.Assertions.assertThat;
import static org.awaitility.Awaitility.await;

@Testcontainers
class MyPipelineIT {

    @Container
    private final VoltSpContainer simulation = VoltSpContainer.newVoltSp("1.7.1")
            .withParallelism(1)
            .withPipelineClass(MyPipeline.class)
            .withVoltLicense(ResourceHelper.getVoltLicenseLocation())
            .withConfigurationYaml("""
                    tps: 100
                    """)
            .withClassesUnder(MavenPaths.mavenClasses())
            .withLoggerName("simulation");

    @Test
    void shouldProduceExpectedOutput() {
        await("for expected output")
                .untilAsserted(() ->
                        assertThat(simulation.getLogs()).contains("EXPECTED OUTPUT"));
    }
}
```

Key points:
- Use `@Testcontainers` on the class and `@Container` on the field — Testcontainers manages start/stop automatically.
- Use Awaitility `await()` instead of `Thread.sleep()` for output assertions.
- Mount classes with `MavenPaths.mavenClasses()` (main) or `MavenPaths.mavenTestClasses()` (test) depending on where the pipeline class lives.
- If you need a custom wait strategy (e.g., `awaitStart(WaitStrategy)`) or ordered multi-container startup, manage the lifecycle manually instead (see multi-container pattern below).

## YAML pipeline test pattern

Test a YAML-defined pipeline without any Java pipeline class:

```java
@Testcontainers
class YamlPipelineIT {

    @Container
    private final VoltSpContainer simulation = VoltSpContainer.newVoltSp("1.7.1")
            .withParallelism(1)
            .withPipelineDefinitionYaml("""
                    version: 1
                    name: "yaml-test"

                    source:
                        collection:
                          elements:
                            - "Hello World"

                    sink:
                        stdout: {}
                    """)
            .withVoltLicense(ResourceHelper.getVoltLicenseLocation())
            .withLoggerName("simulation");

    @Test
    void shouldRunYamlPipeline() {
        await("for output")
                .untilAsserted(() ->
                        assertThat(simulation.getLogs()).contains("Hello World"));
    }
}
```

No `withClassesUnder` or `withAppJar` is needed when the pipeline is defined entirely in YAML with built-in plugins.

## Mounting 3rd-party JARs

When your pipeline depends on libraries not bundled in the VoltSP image:

```java
.with3rdPartyJar("org.apache.commons", "commons-lang3", "3.17.0")
```

This scans the test classpath for the matching JAR and copies it into the container at `/volt-apps/`.

## Mounting data files

Use `WorkingDirPaths` to mount project-relative directories (e.g., ML models, test data):

```java
.withClassesUnder(WorkingDirPaths.resolve("data/models"))
```

## Debugging a container test

Attach a remote debugger to the pipeline running inside the container:

```java
.withDebugger(8000, true)   // suspend=true pauses until debugger attaches
```

Then connect your IDE debugger to `localhost:8000`.

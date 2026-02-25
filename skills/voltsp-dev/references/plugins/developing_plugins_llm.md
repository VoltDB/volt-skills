# VoltSP Plugin Creation Guide (AI Prompt)

## Plugin Types
Source, Sink, Processor, Resource, Emitter

## Core Structure

### 1. Maven Setup
**Location**: `plugins/{plugin-name}/`
**Reference**: `plugins/network/pom.xml` or `plugins/beats/pom.xml`

```xml
<parent>
    <groupId>org.voltdb</groupId>
    <artifactId>plugins</artifactId>
    <version>1.0-SNAPSHOT</version>
</parent>

<artifactId>volt-stream-plugin-{name}</artifactId>

<build>
    <plugins>
        <plugin>
            <groupId>org.voltdb</groupId>
            <artifactId>volt-stream-maven-plugin</artifactId>
        </plugin>
    </plugins>
</build>
```

### 2. Config Record (API)
**Package**: `org.voltdb.stream.plugin.{name}.api`
**Reference Examples**:
- `plugins/network/src/main/java/org/voltdb/stream/plugin/network/api/NetworkSourceConfig.java`
- `plugins/beats/src/main/java/org/voltdb/stream/plugin/beats/api/BeatsSourceConfig.java`
- `plugins/onnx/src/main/java/org/voltdb/stream/plugin/onnx/api/OnnxProcessorConfig.java`

```java
@VoltSP.Documentation(
    description = "The $source$ source does X.",
    configurations = {@Configuration(language = JAVA, code = "..."), @Configuration(language = YAML, code = "...")},
    examples = {@Example(language = JAVA, inline = "...")}
)
@VoltSP.Source(name = "{plugin-name}", implementation = "org.voltdb.stream.plugin.{name}.{Name}Source")
public record MySourceConfig<T>(
    @Field(description = "...", required = true) HostAndPort address,
    @Field(description = "...", defaultValue = "30s") Duration timeout,
    @Field(description = "...", required = true) Decoder<T> decoder,
    @Field(description = "...") Map<String, String> options,
    @Field(description = "...") ExceptionHandler exceptionHandler
) {}
```

**Annotations**:
- `@VoltSP.{Source|Sink|Processor|Resource|Emitter}(name, implementation)`
- `@Field(description, required=true, defaultValue="30s")` - Duration defaults: "30s", "5m", "PT1H"

**Supported Types**: Primitives, `HostAndPort`, `Duration`, `Decoder<T>`, `ExceptionHandler`, `VoltStreamResourceReference`, `Map<String,String>`, `List<String>`, custom enums/classes

### 3. Implementation
**Package**: `org.voltdb.stream.plugin.{name}`
**Reference Examples**:
- Source: `plugins/network/src/main/java/org/voltdb/stream/plugin/network/NetworkSource.java`
- Sink: `plugins/network/src/main/java/org/voltdb/stream/plugin/network/NetworkSink.java`
- Processor: `plugins/onnx/src/main/java/org/voltdb/stream/plugin/onnx/OnnxProcessor.java`

**Constructor**: `public MySource(Logger logger, MySourceConfig<T> config)`

**Interfaces**:
| Type | Interface | Key Methods |
|------|-----------|------------|
| Source | `VoltStreamSource<T>` | `configure()`, `process(batchId, consumer, ctx)`, `destroy()` |
| Sink | `VoltStreamSink<T>` | `configure()`, `accept(input, ctx)`, `destroy()` |
| Processor | `VoltStreamFunction<I,O>` | `configure()`, `process(input, consumer, ctx)`, `destroy()` |

**Pattern**:
```java
public class MySource<T> implements VoltStreamSource<T> {
    private final Logger logger;
    private final MySourceConfig<T> config;
    private Tags tags;

    public MySource(Logger logger, MySourceConfig<T> config) {
        this.logger = logger;
        this.config = config;
    }

    @Override
    public void configure(ExecutionContext context) {
        Observer observer = context.observer();
        tags = observer.tags()
            .with(BaseTag.SOURCE, getClass().getSimpleName())
            .with(BaseTag.WORKER, Thread.currentThread().getId())
            .create();
    }

    @Override
    public void process(long batchId, Consumer<T> consumer, ExecutionContext context) {
        // Emit: consumer.consume(item)
        context.observer().increment(BaseMetric.EMITTED, count, tags);
    }

    @Override
    public void destroy(ExecutionContext context) {
        context.observer().expireTags(tags);
    }
}
```

### 4. Common Patterns

**Shared Resources** (`configureOnce`):
```java
server = context.configurator().configureOnce("key", () -> {
    Server s = new Server(); s.start(); return s;
});
```

**Exception Handling**:
```java
ExceptionHandler handler = config.exceptionHandler();
if (handler == null) handler = context.execution()::handleException;
```

**Metrics**:
```java
Tags tags = observer.tags()
    .with(BaseTag.SOURCE, "MySource")
    .with(BaseTag.WORKER, Thread.currentThread().getId())
    .create();
observer.increment(BaseMetric.EMITTED, count, tags);
```

### 5. Testing

**Unit Test** (MainSimulator) - **Reference**: `plugins/network/src/test/java/org/voltdb/stream/plugin/network/ReadFromTCPSocketTest.java`
```java
private MainSimulation simulation;

@AfterEach
void tearDown() { if (simulation != null) simulation.exit(Duration.ofSeconds(10)); }

@Test
void test() {
    LocalConfiguration config = LocalConfigurationFactory.forSimulation()
        .setPipeline(TestPipeline.class)
        .setProperty("source.plugin.key", "value")
        .setConfigYaml("source:\n  plugin:\n    option: val");

    simulation = MainSimulator.fork(config);

    await().untilAsserted(() -> {
        List<String> results = simulation.getPipelineInstance(TestPipeline.class).getCollectedItems();
        assertThat(results).contains("expected");
    });
}
```

**Test Pipeline** (uses `MemorySink`):
```java
public class TestPipeline implements VoltPipeline {
    private final MemorySink<String> sink = Sinks.collection();

    @Override
    public void define(VoltStreamBuilder stream) {
        stream.consumeFromSource(MySourceConfigBuilder.<String>builder()
                .withDecoder(Decoders.toLinesDecoder()))
              .terminateWithSink(sink);
    }

    public List<String> getCollectedItems() { return sink.copy(); }
}
```

**E2E Test** (VoltSpContainer) - **Reference**: `volt-stream-e2e-tests/src/test/java/org/voltdb/stream/e2e/RateLimitedGeneratorE2ETest.java`
```java
@ExtendWith(StreamEnvExtension.class)
class E2ETest {
    @VoltSp
    VoltSpContainer voltsp;

    @Test
    void test() {
        voltsp.withPipelineDefinitionYaml("version: 1\nname: test\nsource:...\nsink:...").start();
        await().untilAsserted(() -> assertThat(voltsp.getLogs()).contains("expected"));
    }
}
```

**Container Annotations**:
- `@VoltSp` - VoltSpContainer (not auto-started)
- `@ElasticsearchTestContainer(value = "es")` - ElasticsearchContainer
- `@KafkaTestContainer(value = "kafka")` - KafkaContainer
- `@SyslogTestContainer`, `@SchemaRegistryTestContainer`, `@VoltClusterTestContainer`

Containers share Docker network, reference by alias: `"kafka:9092"`, `"es:9200"`

### 6. Build & Checklist

**Build**: `mvn clean install` (generates `{Name}ConfigBuilder` class)

**Generated Builder**:
```java
MySourceConfigBuilder.<String>builder()
    .withAddress("0.0.0.0", 123)
    .withTimeout(30, TimeUnit.SECONDS)
    .withDecoder(Decoders.toLinesDecoder())
    .addOptionsEntry("key", "value")
    .build();
```

**Checklist**:
- [ ] Create `plugins/{name}/` with minimal pom.xml
- [ ] Add to `plugins/pom.xml` modules list
- [ ] Config record in `.api` package with annotations
- [ ] Implementation class with constructor, interfaces
- [ ] Unit tests using MainSimulator + test pipeline with MemorySink
- [ ] Files end with newline
- [ ] Optimize imports, fix IntelliJ warnings
- [ ] Run `mvn clean install`

**Key Rules**:
- Use `Awaitility.await()` in tests, never `Thread.sleep()`
- `@VoltSp` requires manual `.start()`
- Test references: `plugins/{beats,network,onnx}/src/test/java/`, `volt-stream-e2e-tests/src/test/java/`

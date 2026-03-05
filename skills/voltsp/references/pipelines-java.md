# Pipelines (Java DSL)

Use this when defining pipelines as Java classes that implement `VoltPipeline`.

## Prerequisites

VoltSP publishes its APIs to the maven central. These are required to compile pipelines
and use sink/source/processor plugins. The groupId of the jars is `org.voltdb` and
artifact id starts with `volt-stream-`. At a minimum you need to have `org.voltdb:volt-stream-api` and `org.voltdb:volt-stream-connectors-api` dependencies.

For Maven project setup and a starter `pom.xml`, read `references/maven-setup.md`.

## Core shape

Always wire the stream in this order:

1. `consumeFromSource(...)`
2. zero or more `processWith(...)`
3. `terminateWithSink(...)`

Minimal pattern:

```java
import org.voltdb.stream.api.ExecutionContext.ConfigurationContext;
import org.voltdb.stream.api.Sinks;
import org.voltdb.stream.api.Sources;
import org.voltdb.stream.api.pipeline.VoltPipeline;
import org.voltdb.stream.api.pipeline.VoltStreamBuilder;

public final class ExamplePipeline implements VoltPipeline {
  @Override
  public void define(VoltStreamBuilder stream) {
    ConfigurationContext config = stream.getExecutionContext().configurator();
    int tps = config.findByPath("generator.tps").orElse(10);

    stream
      .withName("example-pipeline")
      .consumeFromSource(Sources.generateAtRate(tps, () -> "hello\n"))
      .processWith(String::toUpperCase)
      .terminateWithSink(Sinks.stdout());
  }
}
```

## Error routing and alternate sinks

- Configure global handling with `stream.onError().setExceptionHandler(...)`.
- Add named sinks with `stream.onError().addNamedSink("sinkName", configurator)`.
- Route records to named sinks with `context.execution().emit("sinkName", record)`.
- Asynchronous commits can use `nextCommitResult()`.
- Tune async commit timeout with `voltsp.commit.async.timeout.ms` when default timeout is too strict for downstream latency.

## Configuration boundary

- Keep environment values in runtime config (`--config`, Helm `streaming.pipeline.configuration`).
- Read config from `stream.getExecutionContext().configurator().findByPath(...)`.
- For builders that support auto-configuration, prefer reading common operator settings from config and override only values that must remain programmatic.
- If both config and Java DSL set the same property, Java DSL wins.

Read `references/configuration.md` for interpolation/secrets details.

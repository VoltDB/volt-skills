# Pipelines (Java DSL)

Use this when writing a pipeline in Java.

## Project bootstrap (optional)

If you have access to the VoltSP Maven archetype:

```shell
mvn archetype:generate                                 \
    -DarchetypeGroupId=org.voltdb                      \
    -DarchetypeArtifactId=volt-stream-maven-quickstart \
    -DarchetypeVersion=<voltsp-version>
```

## Pipeline shape

- Implement `org.voltdb.stream.api.pipeline.VoltPipeline`.
- Wire the stream as: `consumeFromSource(...) -> processWith(...) -> terminateWithSink(...)`.

Minimal example (stdin -> uppercase -> stdout):

```java
import org.voltdb.stream.api.ExecutionContext;
import org.voltdb.stream.api.Sinks;
import org.voltdb.stream.api.Sources;
import org.voltdb.stream.api.pipeline.VoltPipeline;
import org.voltdb.stream.api.pipeline.VoltStreamBuilder;

public final class StdinToStdout implements VoltPipeline {
  @Override
  public void define(VoltStreamBuilder stream) {
    ExecutionContext.ConfigurationContext cfg = stream.getExecutionContext().configurator();
    int tps = cfg.findByPath("tps").orElse(10);

    stream
      .consumeFromSource(Sources.generateAtRate(tps, () -> "hello\n"))
      .processWith(String::toUpperCase)
      .terminateWithSink(Sinks.stdout());
  }
}
```

## Configuration: keep env-specific values out of code

- CLI: pass config YAML with `--config` (and `--configSecure` for secrets).
- Kubernetes/Helm: put values under `streaming.pipeline.configuration`: see `references/kubernetes.md`.

## Packaging and dependencies

- Build your app JAR: `mvn clean package` (produces `target/*.jar`).
- If you rely on VoltSP-provided connectors/plugins, keep those dependencies as `scope=provided` so your app compiles but you don’t ship duplicates.

## “Inline operator” vs “plugin”

- Inline (in the pipeline JAR) for one-off logic.
- Prefer a reusable plugin when the operator needs to be shared across pipelines/teams or shipped separately: see `references/plugins.md`.

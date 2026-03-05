# Stdout Sink

Write records to standard output for debugging and observability.

Compile dependency: volt-stream-connectors-api

## Java Example

```java
import org.voltdb.stream.api.Sinks;

stream.terminateWithSink(Sinks.stdout());
```

## YAML Example

```yaml
sink:
  stdout: { }
```

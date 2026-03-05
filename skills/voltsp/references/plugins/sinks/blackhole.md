# Blackhole Sink

Drop records intentionally for baseline throughput and smoke tests.

Compile dependency: volt-stream-connectors-api

## Java Example

```java
import org.voltdb.stream.api.Sinks;

stream.terminateWithSink(Sinks.blackhole());
```

## YAML Example

```yaml
sink:
  blackhole: { }
```

## Properties

None

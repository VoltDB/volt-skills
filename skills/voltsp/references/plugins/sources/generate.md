# Generator Source

Generate synthetic data from a supplier function for performance testing and demos. Supports rate-limited generation and automatic stop after a max event count.

Compile dependency: volt-stream-connectors-api

## Java Example

Generate records as fast as possible:

```java
import org.voltdb.stream.api.Sources;

stream.consumeFromSource(Sources.generate(() -> "event-" + System.nanoTime()));
```

Generate records at a fixed rate (transactions per second):

```java
import org.voltdb.stream.api.Sources;

stream.consumeFromSource(Sources.generateAtRate(1000.0, () -> "event-" + System.nanoTime()));
```

Generate records at a fixed rate with a counter:

```java
import org.voltdb.stream.api.Sources;

stream.consumeFromSource(Sources.generateAtRate(1000.0, counter -> "event-" + counter));
```

## YAML Example

```yaml
source:
  generate:
    tps: 10
    eventsPerBatch: 1
    maxEventCount: 10
    generator: |
      function process(input) {
        return "Hello World " + input + "\n";
      }
```

## Properties
- int tps: Target transactions per second.
- int eventsPerBatch: Number of events generated per batch, independent of TPS.
- int maxEventCount: Total events to generate before the pipeline stops automatically.
- String generator: JavaScript function or Java method reference that produces records. Receives the event counter as input.

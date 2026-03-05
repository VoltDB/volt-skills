# Generator Source

Generate synthetic data from a supplier function for performance testing and demos. Supports rate-limited generation.

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

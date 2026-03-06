# Collection Source

Emit deterministic in-memory elements, ideal for tests and demos.

Compile dependency: volt-stream-connectors-api

## Java Example

```java
import org.voltdb.stream.api.Sources;

stream.consumeFromSource(Sources.collection("item1", "item2", "item3"));
```

## YAML Example

```yaml
source:
  collection:
    elements:
      - "item1"
      - "item2"
      - "item3"
```

## Properties
- List&lt;T&gt; elements: In-memory elements to emit, required.

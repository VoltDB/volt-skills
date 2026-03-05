# Stdin Source

Read line-delimited records from standard input for local runs and debugging.

Compile dependency: volt-stream-connectors-api

## Java Example

```java
import org.voltdb.stream.api.Sources;

stream.consumeFromSource(Sources.stdin());
```

## YAML Example

```yaml
source:
  stdin: { }
```

# File Source

Read line-delimited records from a file.

Compile dependency: volt-stream-connectors-api

## Java Example

```java
import org.voltdb.stream.api.Sources;

stream.consumeFromSource(Sources.file("/path/to/input.txt"));
```

## YAML Example

```yaml
source:
  file:
    path: "/path/to/input.txt"
```

## Properties
- String path: Path to the input file, required.

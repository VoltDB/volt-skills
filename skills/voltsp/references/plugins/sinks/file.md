# File Sink

A sink that writes streamed data items to a file within a specified directory.
Each instance creates a new file with a unique name in the designated directory.
Data items are encoded into bytes and written to the file, each separated by a specified line terminator.

Compile dependency: volt-stream-connectors-api

## Java Example

Creates a sink that writes data items to files in a specified directory.

```java
import org.voltdb.stream.api.Sinks;

stream.terminateWithSink(Sinks.directory(...));
```

## YAML Example

```yaml
sink:
  file:
    dirPath: "/path/to/output/directory"
```

## Properties
- String dirPath: Path to the output directory, required.
- String delimiter: Event delimiter that will be appended to the file between writing consecutive events.
- Function<T, byte[]> encoder: Code that converts incoming elements to bytes for writing into the file.

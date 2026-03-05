# Java Processor

Execute dynamically provided Java code on streamed data. Supports inline source code or loading from a URI.

Compile dependency: volt-stream-plugin-java-api

## Java Example

```java
import org.voltdb.stream.plugin.java.api.JavaProcessorConfigBuilder;

stream.processWith(JavaProcessorConfigBuilder.builder()
    .withSource("""
        public class MyProc {
            public static Object process(Object input) {
                return String.valueOf(input).toUpperCase();
            }
        }
        """)
);
```

## YAML Example

```yaml
processors:
  - java:
      source: |
        public class MyProc {
          public static Object process(Object input) {
            return String.valueOf(input).toUpperCase();
          }
        }
```

Or load from a URI:

```yaml
processors:
  - java:
      sourceUri: "file:///path/to/MyProcessor.java"
```

## Properties
- String source: Java source code to compile and execute.
- URI sourceUri: URI to a Java source file.

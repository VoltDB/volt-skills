# JavaScript Processor

Run JavaScript transformations and filters inline in the pipeline using GraalVM JavaScript engine.

Compile dependency: volt-stream-plugin-javascript-api

## Java Example

```java
import org.voltdb.stream.plugin.javascript.api.JavaScriptProcessorConfigBuilder;

stream.processWith(JavaScriptProcessorConfigBuilder.builder()
    .withScript("""
        function process(input) {
            return input.toUpperCase();
        }
        """)
);
```

## YAML Example

```yaml
processors:
  - javascript:
      script: |
        function process(input) {
          if (typeof input === 'string') {
            return input.toUpperCase();
          }
          return input;
        }
```

Or load from a URI:

```yaml
processors:
  - javascript:
      scriptUrl: "file:///path/to/transform.js"
```

## Properties
- String script: JavaScript code to execute.
- URI scriptUrl: URL to a JavaScript file.

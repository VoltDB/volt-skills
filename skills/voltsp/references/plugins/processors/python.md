# Python Processor

Execute Python-based transformation logic using GraalVM Python engine. The script must define a `process()` function.

Compile dependency: volt-stream-plugin-python-api

## Java Example

```java
import org.voltdb.stream.plugin.python.api.PythonProcessorConfigBuilder;

stream.processWith(PythonProcessorConfigBuilder.builder()
    .withScript("""
        def process(input):
            return input.upper()
        """)
    .withTimeout(Duration.ofSeconds(2))
);
```

## YAML Example

```yaml
processors:
  - python:
      script: |
        def process(input):
            return input.upper()
      timeout: "PT2S"
```

Or load from a URL:

```yaml
processors:
  - python:
      scriptUrl: "file:///path/to/transform.py"
```

## Properties
- String script: Python code to execute (must define a `process()` function).
- URI scriptUrl: URL to a Python script file.
- Duration timeout: Max execution time per invocation, default 1s.

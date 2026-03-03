# Pipeline Logging Configuration

## Goal

Set global and package-level logging from pipeline YAML and verify behavior in runtime logs.

## YAML shape

```yaml
version: 1
name: "logging-test"

source:
  collection:
    elements: ["Hello world!"]

sink:
  stdout: {}

logging:
  globalLevel: "TRACE"
  loggers:
    "org.voltdb": "DEBUG"
```

## Notes

- YAML logging config is useful for runtime behavior checks.
- For startup-time logging, still rely on CLI/Helm JVM/log settings when needed.

# Python Processor (Processor)

## Purpose

Execute Python-based transformation logic.

Compile dependency:

- org.voltdb:volt-stream-plugin-python-api

## When To Use

- Transform, enrich, or filter records between source and sink.
- Externalize model/script/class parameters through runtime config.

## When To Avoid

- Avoid if a plain Java lambda/function is simpler and more maintainable.
- Avoid embedding large scripts/models inline when they should be versioned assets.

## Java Example

```java
stream.processWith(
    /* Use Python Processor builder/configurator for 'python' */
);
```

## YAML Example

```yaml
processors:
  - python:
      # plugin-specific fields
```

## Runtime Config Keys

- Pipeline-definition path: `processors[].python`
- Helm auto-config path: `streaming.pipeline.configuration.processors.python`
- Keep secrets in secure config overlays.

## Helm Notes

- Keep model/script/class values configurable by environment.
- Check CPU/memory requirements for heavy processor workloads.

## Testing Checks

- Unit-test transformation behavior with deterministic fixtures.
- Add integration checks around plugin runtime requirements.
- Verify null/filter semantics where processor intentionally drops events.

## Common Failures

- Invalid processor-specific field types in YAML.
- Missing runtime dependencies for script/model execution.
- Python runtime/dependency packaging mismatch at deployment time.

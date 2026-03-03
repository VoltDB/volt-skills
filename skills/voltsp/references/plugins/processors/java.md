# Java Processor (Processor)

## Purpose

Execute Java class-based processor logic via plugin configuration.

Compile dependency:

- org.voltdb:volt-stream-plugin-java-api

## When To Use

- Transform, enrich, or filter records between source and sink.
- Externalize model/script/class parameters through runtime config.

## When To Avoid

- Avoid if a plain Java lambda/function is simpler and more maintainable.
- Avoid embedding large scripts/models inline when they should be versioned assets.

## Java Example

```java
stream.processWith(
    /* Use Java Processor builder/configurator for 'java' */
);
```

## YAML Example

```yaml
processors:
  - java:
      # plugin-specific fields
```

## Runtime Config Keys

- Pipeline-definition path: `processors[].java`
- Helm auto-config path: `streaming.pipeline.configuration.processors.java`
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
- Processor class loading issues from classpath/jar packaging mistakes.

# Collection Source (Source)

## Purpose

Emit deterministic in-memory elements, ideal for tests and demos.

Compile dependency:

- built-in (volt-stream-connectors-api)

## When To Use

- Start pipeline ingestion from this external/input system.
- Keep source configuration externalized via runtime config and Helm values.

## When To Avoid

- Avoid when a lower-complexity source already satisfies the workflow.
- Avoid embedding environment-specific endpoints directly in Java code.

## Java Example

```java
stream.consumeFromSource(
    /* Use Collection Source builder/configurator for 'collection' */
);
```

## YAML Example

```yaml
source:
  collection:
    # plugin-specific fields
```

## Runtime Config Keys

- Pipeline-definition path: `source.collection`
- Helm auto-config path: `streaming.pipeline.configuration.source.collection`
- Use secure overlays (`--configSecure` / `configurationSecure`) for credentials.

## Helm Notes

- Put source settings under `streaming.pipeline.configuration.source.collection`.
- If Java code sets the same field, Java DSL value takes precedence.

## Testing Checks

- Confirm startup does not fail on missing required fields.
- Validate restart behavior and duplicate-handling expectations for this source.
- Assert expected throughput/latency under representative input rates.

## Common Failures

- Misconfigured required fields in `source.collection`.
- Classpath/dependency mismatch for this plugin artifact.
- Large in-memory payloads can distort throughput/perf expectations.

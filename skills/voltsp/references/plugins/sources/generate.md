# Generator Source (Source)

## Purpose

Generate synthetic traffic at configured rates for performance or demo flows.

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
    /* Use Generator Source builder/configurator for 'generate' */
);
```

## YAML Example

```yaml
source:
  generate:
    # plugin-specific fields
```

## Runtime Config Keys

- Pipeline-definition path: `source.generate`
- Helm auto-config path: `streaming.pipeline.configuration.source.generate`
- Use secure overlays (`--configSecure` / `configurationSecure`) for credentials.

## Helm Notes

- Put source settings under `streaming.pipeline.configuration.source.generate`.
- If Java code sets the same field, Java DSL value takes precedence.

## Testing Checks

- Confirm startup does not fail on missing required fields.
- Validate restart behavior and duplicate-handling expectations for this source.
- Assert expected throughput/latency under representative input rates.

## Common Failures

- Misconfigured required fields in `source.generate`.
- Classpath/dependency mismatch for this plugin artifact.
- Configured rate is too high for downstream capacity, causing backpressure.

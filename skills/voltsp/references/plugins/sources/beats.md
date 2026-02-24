# Beats Source (Source)

## Purpose

Ingest events from Elastic Beats agents.

Compile dependency:

- org.voltdb:volt-stream-plugin-beats-api

## When To Use

- Start pipeline ingestion from this external/input system.
- Keep source configuration externalized via runtime config and Helm values.

## When To Avoid

- Avoid when a lower-complexity source already satisfies the workflow.
- Avoid embedding environment-specific endpoints directly in Java code.

## Java Example

```java
stream.consumeFromSource(
    /* Use Beats Source builder/configurator for 'beats' */
);
```

## YAML Example

```yaml
source:
  beats:
    # plugin-specific fields
```

## Runtime Config Keys

- Pipeline-definition path: `source.beats`
- Helm auto-config path: `streaming.pipeline.configuration.source.beats`
- Use secure overlays (`--configSecure` / `configurationSecure`) for credentials.

## Helm Notes

- Put source settings under `streaming.pipeline.configuration.source.beats`.
- If Java code sets the same field, Java DSL value takes precedence.

## Testing Checks

- Confirm startup does not fail on missing required fields.
- Validate restart behavior and duplicate-handling expectations for this source.
- Assert expected throughput/latency under representative input rates.

## Common Failures

- Misconfigured required fields in `source.beats`.
- Classpath/dependency mismatch for this plugin artifact.
- Beats version/format mismatch with expected decoder and mapping.

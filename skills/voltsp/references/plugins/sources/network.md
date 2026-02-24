# Network Source (Source)

## Purpose

Ingest UDP/TCP records from network endpoints.

Compile dependency:

- org.voltdb:volt-stream-plugin-network-api

## When To Use

- Start pipeline ingestion from this external/input system.
- Keep source configuration externalized via runtime config and Helm values.

## When To Avoid

- Avoid when a lower-complexity source already satisfies the workflow.
- Avoid embedding environment-specific endpoints directly in Java code.

## Java Example

```java
stream.consumeFromSource(
    /* Use Network Source builder/configurator for 'network' */
);
```

## YAML Example

```yaml
source:
  network:
    # plugin-specific fields
```

## Runtime Config Keys

- Pipeline-definition path: `source.network`
- Helm auto-config path: `streaming.pipeline.configuration.source.network`
- Use secure overlays (`--configSecure` / `configurationSecure`) for credentials.

## Helm Notes

- Put source settings under `streaming.pipeline.configuration.source.network`.
- If Java code sets the same field, Java DSL value takes precedence.

## Testing Checks

- Confirm startup does not fail on missing required fields.
- Validate restart behavior and duplicate-handling expectations for this source.
- Assert expected throughput/latency under representative input rates.

## Common Failures

- Misconfigured required fields in `source.network`.
- Classpath/dependency mismatch for this plugin artifact.
- Protocol/address/decoder mismatch causes dropped or malformed records.

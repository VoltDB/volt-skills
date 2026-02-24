# Kafka Source (Source)

## Purpose

Consume records from Kafka topics with group/offset controls.

Compile dependency:

- org.voltdb:volt-stream-plugin-kafka-api

## When To Use

- Start pipeline ingestion from this external/input system.
- Keep source configuration externalized via runtime config and Helm values.

## When To Avoid

- Avoid when a lower-complexity source already satisfies the workflow.
- Avoid embedding environment-specific endpoints directly in Java code.

## Java Example

```java
stream.consumeFromSource(
    /* Use Kafka Source builder/configurator for 'kafka' */
);
```

## YAML Example

```yaml
source:
  kafka:
    # plugin-specific fields
```

## Runtime Config Keys

- Pipeline-definition path: `source.kafka`
- Helm auto-config path: `streaming.pipeline.configuration.source.kafka`
- Use secure overlays (`--configSecure` / `configurationSecure`) for credentials.

## Helm Notes

- Put source settings under `streaming.pipeline.configuration.source.kafka`.
- If Java code sets the same field, Java DSL value takes precedence.

## Testing Checks

- Confirm startup does not fail on missing required fields.
- Validate restart behavior and duplicate-handling expectations for this source.
- Assert expected throughput/latency under representative input rates.

## Common Failures

- Misconfigured required fields in `source.kafka`.
- Classpath/dependency mismatch for this plugin artifact.
- Deserializer, topic, or group settings do not match actual Kafka data layout.

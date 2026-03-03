# MQTT Source (Source)

## Purpose

Subscribe to MQTT topics for IoT/event workloads.

Compile dependency:

- org.voltdb:volt-stream-plugin-mqtt-api

## When To Use

- Start pipeline ingestion from this external/input system.
- Keep source configuration externalized via runtime config and Helm values.

## When To Avoid

- Avoid when a lower-complexity source already satisfies the workflow.
- Avoid embedding environment-specific endpoints directly in Java code.

## Java Example

```java
stream.consumeFromSource(
    /* Use MQTT Source builder/configurator for 'mqtt' */
);
```

## YAML Example

```yaml
source:
  mqtt:
    # plugin-specific fields
```

## Runtime Config Keys

- Pipeline-definition path: `source.mqtt`
- Helm auto-config path: `streaming.pipeline.configuration.source.mqtt`
- Use secure overlays (`--configSecure` / `configurationSecure`) for credentials.

## Helm Notes

- Put source settings under `streaming.pipeline.configuration.source.mqtt`.
- If Java code sets the same field, Java DSL value takes precedence.

## Testing Checks

- Confirm startup does not fail on missing required fields.
- Validate restart behavior and duplicate-handling expectations for this source.
- Assert expected throughput/latency under representative input rates.

## Common Failures

- Misconfigured required fields in `source.mqtt`.
- Classpath/dependency mismatch for this plugin artifact.
- QoS/topic filter or broker auth mismatch prevents stable consumption.

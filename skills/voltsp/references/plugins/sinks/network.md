# Network Sink (Sink)

## Purpose

Emit processed data over UDP/TCP to external consumers.

Compile dependency:

- org.voltdb:volt-stream-plugin-network-api

## When To Use

- Deliver processed records to this external target.
- Keep sink destinations and credentials outside pipeline code.

## When To Avoid

- Avoid when sink guarantees do not match your delivery semantics.
- Avoid mixing sink-specific credentials into non-secure config files.

## Java Example

```java
stream.terminateWithSink(
    /* Use Network Sink builder/configurator for 'network' */
);
```

## YAML Example

```yaml
sink:
  network:
    # plugin-specific fields
```

## Runtime Config Keys

- Pipeline-definition path: `sink.network`
- Helm auto-config path: `streaming.pipeline.configuration.sink.network`
- Secure values: `--configSecure` or `streaming.pipeline.configurationSecure`

## Helm Notes

- Place sink settings under `streaming.pipeline.configuration.sink.network`.
- Keep sink endpoint/topic/index names configurable by environment.

## Testing Checks

- Validate commit/retry behavior for sink failures.
- Validate idempotency/duplicate behavior at sink boundary.
- Assert observability signals (logs/metrics) for sink commit outcomes.

## Common Failures

- Missing sink-required fields.
- Serialization/schema mismatch between record type and sink expectation.
- Transport expectations (UDP loss, TCP framing) not matched by receivers.

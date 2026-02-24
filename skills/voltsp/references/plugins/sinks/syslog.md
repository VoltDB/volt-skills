# Syslog Sink (Sink)

## Purpose

Forward records to remote syslog endpoints (RFC3164 style).

Compile dependency:

- org.voltdb:volt-stream-plugin-syslog-api

## When To Use

- Deliver processed records to this external target.
- Keep sink destinations and credentials outside pipeline code.

## When To Avoid

- Avoid when sink guarantees do not match your delivery semantics.
- Avoid mixing sink-specific credentials into non-secure config files.

## Java Example

```java
stream.terminateWithSink(
    /* Use Syslog Sink builder/configurator for 'syslog' */
);
```

## YAML Example

```yaml
sink:
  syslog:
    # plugin-specific fields
```

## Runtime Config Keys

- Pipeline-definition path: `sink.syslog`
- Helm auto-config path: `streaming.pipeline.configuration.sink.syslog`
- Secure values: `--configSecure` or `streaming.pipeline.configurationSecure`

## Helm Notes

- Place sink settings under `streaming.pipeline.configuration.sink.syslog`.
- Keep sink endpoint/topic/index names configurable by environment.

## Testing Checks

- Validate commit/retry behavior for sink failures.
- Validate idempotency/duplicate behavior at sink boundary.
- Assert observability signals (logs/metrics) for sink commit outcomes.

## Common Failures

- Missing sink-required fields.
- Serialization/schema mismatch between record type and sink expectation.
- Format/facility expectations differ from downstream SIEM parsing rules.

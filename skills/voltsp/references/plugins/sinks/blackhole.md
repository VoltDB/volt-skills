# Blackhole Sink (Sink)

## Purpose

Drop records intentionally for baseline throughput and smoke tests.

Compile dependency:

- built-in (volt-stream-connectors-api)

## When To Use

- Deliver processed records to this external target.
- Keep sink destinations and credentials outside pipeline code.

## When To Avoid

- Avoid when sink guarantees do not match your delivery semantics.
- Avoid mixing sink-specific credentials into non-secure config files.

## Java Example

```java
stream.terminateWithSink(
    /* Use Blackhole Sink builder/configurator for 'blackhole' */
);
```

## YAML Example

```yaml
sink:
  blackhole:
    # plugin-specific fields
```

## Runtime Config Keys

- Pipeline-definition path: `sink.blackhole`
- Helm auto-config path: `streaming.pipeline.configuration.sink.blackhole`
- Secure values: `--configSecure` or `streaming.pipeline.configurationSecure`

## Helm Notes

- Place sink settings under `streaming.pipeline.configuration.sink.blackhole`.
- Keep sink endpoint/topic/index names configurable by environment.

## Testing Checks

- Validate commit/retry behavior for sink failures.
- Validate idempotency/duplicate behavior at sink boundary.
- Assert observability signals (logs/metrics) for sink commit outcomes.

## Common Failures

- Missing sink-required fields.
- Serialization/schema mismatch between record type and sink expectation.
- Using blackhole in production by mistake masks delivery failures.

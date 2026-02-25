# VoltDB Bulk Insert Sink (Sink)

## Purpose

Batch-insert rows into VoltDB for high-throughput ingestion.

Compile dependency:

- org.voltdb:volt-stream-plugin-volt-api

## When To Use

- Deliver processed records to this external target.
- Keep sink destinations and credentials outside pipeline code.

## When To Avoid

- Avoid when sink guarantees do not match your delivery semantics.
- Avoid mixing sink-specific credentials into non-secure config files.

## Java Example

```java
stream.terminateWithSink(
    /* Use VoltDB Bulk Insert Sink builder/configurator for 'voltdb-bulk-insert' */
);
```

## YAML Example

```yaml
sink:
  voltdb-bulk-insert:
    # plugin-specific fields
```

## Runtime Config Keys

- Pipeline-definition path: `sink.voltdb-bulk-insert`
- Helm auto-config path: `streaming.pipeline.configuration.sink.voltdb-bulk-insert`
- Secure values: `--configSecure` or `streaming.pipeline.configurationSecure`

## Helm Notes

- Place sink settings under `streaming.pipeline.configuration.sink.voltdb-bulk-insert`.
- Keep sink endpoint/topic/index names configurable by environment.

## Testing Checks

- Validate commit/retry behavior for sink failures.
- Validate idempotency/duplicate behavior at sink boundary.
- Assert observability signals (logs/metrics) for sink commit outcomes.

## Common Failures

- Missing sink-required fields.
- Serialization/schema mismatch between record type and sink expectation.
- Schema/table mapping and batch sizing are not tuned for workload characteristics.

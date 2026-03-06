# VoltDB Bulk Insert Sink

Batch-insert rows into VoltDB for high-throughput ingestion. Supports INSERT and UPSERT operations with configurable batch sizes and flush intervals.

Compile dependency: volt-stream-plugin-volt-api

## Java Example

```java
import org.voltdb.stream.plugin.volt.api.VoltSinks;

stream.terminateWithSink(VoltSinks.batchedInsert()
    .withVoltClientResource("primary-cluster")
    .withBatchSize(100000)
    .withFlushInterval(Duration.ofSeconds(5))
    .withOperationType(VoltBulkOperationType.INSERT)
);
```

## YAML Example

```yaml
sink:
  voltdb-bulk-insert:
    voltClientResource: "primary-cluster"
    batchSize: 100000
    flushInterval: "PT5S"
    operationType: "INSERT"
```

## Properties
- VoltStreamResourceReference voltClientResource: Reference to a VoltDB client resource, required.
- VoltBulkOperationType operationType: INSERT or UPSERT, default INSERT.
- int batchSize: Number of rows per batch, default 100000.
- Duration flushInterval: Time between automatic flushes, default 1s.

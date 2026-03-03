# Network To Volt Topic Bridge

## Goal

Split the flow into two deployable pipelines:
- Producer: UDP -> VoltDB bulk insert (`logs_stream` table)
- Consumer: Kafka topic exported from VoltDB -> conditional routing to Syslog/Elastic

## Stage 1 (producer)

1. Configure `voltdb-client` resource.
2. Ingest from `source.network`.
3. Map to `VoltTableInsertRequest`.
4. Write via `voltdb-bulk-insert`.

Runtime config example:

```yaml
resources:
- name: primary-cluster
  voltdb-client:
    servers: "host-0:21212"

source:
  network:
    type: udp
    address: "0.0.0.0:15140"

sink:
  voltdb-bulk-insert:
    voltClientResource: primary-cluster
    batchSize: 1
```

## Stage 2 (consumer)

1. Consume from `source.kafka` (`logs_topic`).
2. Process payload and route to syslog or elastic named sink.
3. Keep Kafka source properties in runtime config.

Runtime config example:

```yaml
source:
  kafka:
    bootstrapServers: "host-0:9092"

sink:
  syslog:
    address: "syslog:10514"
  elastic:
    indexName: "logs-index"
    address: "es:9200"
```

## Common pitfalls

- Not enabling/configuring Volt topics in Volt deployment.
- Missing Kafka deserializer settings in Java source builder.
- Using large flush interval without understanding end-to-end latency impact.

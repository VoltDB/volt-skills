# VoltSP Plugin Catalog

This catalog is derived from operator annotations in the Volt Stream codebase (`@VoltSP.Source`, `@VoltSP.Sink`, `@VoltSP.Processor`).

## Detailed coverage (priority set)

These operators have dedicated files under `references/plugins/`.

| Operator | Type | Compile dependency | Config path | Detail file | Notes |
|---|---|---|---|---|---|
| `stdin` | source | built-in (`volt-stream-connectors-api`) | `source.stdin` | `references/plugins/sources/stdin.md` | Interactive and local debugging input |
| `file` | source | built-in (`volt-stream-connectors-api`) | `source.file` | `references/plugins/sources/file.md` | Line-based file ingestion |
| `collection` | source | built-in (`volt-stream-connectors-api`) | `source.collection` | `references/plugins/sources/collection.md` | Deterministic in-memory test data |
| `generate` | source | built-in (`volt-stream-connectors-api`) | `source.generate` | `references/plugins/sources/generate.md` | Rate-limited synthetic load |
| `kafka` | source | `org.voltdb:volt-stream-plugin-kafka-api` | `source.kafka` | `references/plugins/sources/kafka.md` | Durable stream ingestion |
| `network` | source | `org.voltdb:volt-stream-plugin-network-api` | `source.network` | `references/plugins/sources/network.md` | UDP/TCP socket ingestion |
| `mqtt` | source | `org.voltdb:volt-stream-plugin-mqtt-api` | `source.mqtt` | `references/plugins/sources/mqtt.md` | MQTT topic subscription |
| `beats` | source | `org.voltdb:volt-stream-plugin-beats-api` | `source.beats` | `references/plugins/sources/beats.md` | Elastic Beats ingestion |
| `stdout` | sink | built-in (`volt-stream-connectors-api`) | `sink.stdout` | `references/plugins/sinks/stdout.md` | Fast observability sink |
| `blackhole` | sink | built-in (`volt-stream-connectors-api`) | `sink.blackhole` | `references/plugins/sinks/blackhole.md` | Throughput and pipeline smoke tests |
| `file` | sink | built-in (`volt-stream-connectors-api`) | `sink.file` | `references/plugins/sinks/file.md` | Rotating file output |
| `kafka` | sink | `org.voltdb:volt-stream-plugin-kafka-api` | `sink.kafka` | `references/plugins/sinks/kafka.md` | Event publication to Kafka |
| `network` | sink | `org.voltdb:volt-stream-plugin-network-api` | `sink.network` | `references/plugins/sinks/network.md` | UDP/TCP output |
| `elastic` | sink | `org.voltdb:volt-stream-plugin-elastic-api` | `sink.elastic` | `references/plugins/sinks/elastic.md` | Index documents into Elasticsearch |
| `syslog` | sink | `org.voltdb:volt-stream-plugin-syslog-api` | `sink.syslog` | `references/plugins/sinks/syslog.md` | RFC3164 remote logging |
| `mqtt` | sink | `org.voltdb:volt-stream-plugin-mqtt-api` | `sink.mqtt` | `references/plugins/sinks/mqtt.md` | Publish to MQTT broker |
| `voltdb-procedure` | sink | `org.voltdb:volt-stream-plugin-volt-api` | `sink.voltdb-procedure` | `references/plugins/sinks/voltdb-procedure.md` | Transactional procedure calls |
| `voltdb-bulk-insert` | sink | `org.voltdb:volt-stream-plugin-volt-api` | `sink.voltdb-bulk-insert` | `references/plugins/sinks/voltdb-bulk-insert.md` | High-throughput bulk writes |
| `javascript` | processor | `org.voltdb:volt-stream-plugin-javascript-api` | `processors[].javascript` | `references/plugins/processors/javascript.md` | Inline transformation/filter logic |
| `java` | processor | `org.voltdb:volt-stream-plugin-java-api` | `processors[].java` | `references/plugins/processors/java.md` | Class-based processor execution |
| `python` | processor | `org.voltdb:volt-stream-plugin-python-api` | `processors[].python` | `references/plugins/processors/python.md` | Python runtime processing |
| `voltdb-cache` | processor | `org.voltdb:volt-stream-plugin-volt-api` | `processors[].voltdb-cache` | `references/plugins/processors/voltdb-cache.md` | VoltDB-backed enrichment cache |
| `onnx` | processor | `org.voltdb:volt-stream-plugin-onnx-api` | `processors[].onnx` | `references/plugins/processors/onnx.md` | ONNX inference |
| `onnx-genai` | processor | `org.voltdb:volt-stream-plugin-onnx-api` | `processors[].onnx-genai` | `references/plugins/processors/onnx-genai.md` | LLM-style ONNX GenAI inference |

## Catalog-only long tail

These are discoverable in the skill catalog but do not yet have dedicated deep-dive files.

| Operator | Type | Compile dependency | Config path | Why catalog-only for now |
|---|---|---|---|---|
| `appendable` | source | built-in (`volt-stream-connectors-api`) | `source.appendable` | Niche usage outside core pipeline authoring |
| `http` | source | `org.voltdb:volt-stream-plugin-http-api` | `source.http` | Less common than Kafka/network in current workflows |
| `pulsar` | source | `org.voltdb:volt-stream-plugin-pulsar-api` | `source.pulsar` | Environment-specific operator |
| `s3` | source | `org.voltdb:volt-stream-plugin-aws-api` | `source.s3` | Cloud- and policy-dependent setup |
| `s3-sqs-event-listener` | source | `org.voltdb:volt-stream-plugin-aws-api` | `source.s3-sqs-event-listener` | Multi-service AWS integration complexity |
| `voltdb-source` | source | `org.voltdb:volt-stream-plugin-volt-api` | `source.voltdb-source` | Advanced VoltDB pull pattern |
| `memory` | sink | built-in (`volt-stream-connectors-api`) | `sink.memory` | Mostly test-only sink |
| `singlefile` | sink | built-in (`volt-stream-connectors-api`) | `sink.singlefile` | File contention risk under parallelism |
| `http` | sink | `org.voltdb:volt-stream-plugin-http-api` | `sink.http` | Requires HTTP client semantics tuning |
| `iceberg-table` | sink | `org.voltdb:volt-stream-plugin-iceberg-api` | `sink.iceberg-table` | Lakehouse-specific deployments |
| `pulsar` | sink | `org.voltdb:volt-stream-plugin-pulsar-api` | `sink.pulsar` | Less common in current user base |
| `s3` | sink | `org.voltdb:volt-stream-plugin-aws-api` | `sink.s3` | Cloud storage-specific operational concerns |
| `parquet-encoder` | processor | `org.voltdb:volt-stream-plugin-parquet-api` | `processors[].parquet-encoder` | Usually paired with storage-specific sinks |
| `tumbling-count-window` | processor | `org.voltdb:volt-stream-plugin-window-api` | `processors[].tumbling-count-window` | Advanced windowing path |
| `tumbling-time-window` | processor | `org.voltdb:volt-stream-plugin-window-api` | `processors[].tumbling-time-window` | Advanced windowing path |
| `volt-tumbling-count-window` | processor | `org.voltdb:volt-stream-plugin-volt-api` | `processors[].volt-tumbling-count-window` | Remote window execution specialization |
| `volt-tumbling-time-window` | processor | `org.voltdb:volt-stream-plugin-volt-api` | `processors[].volt-tumbling-time-window` | Remote window execution specialization |

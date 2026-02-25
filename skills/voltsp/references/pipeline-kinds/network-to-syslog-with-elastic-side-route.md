# Network To Syslog With Elastic Side Route

## Goal

Ingest UDP records, route selected records to Elasticsearch using a named sink, and send remaining records to Syslog.

## Implementation steps

1. Define a named sink in `stream.onError().addNamedSink("elasticsearch", ...)`.
2. Use `network` source with byte decoder.
3. Convert bytes to string and apply routing processor:
- if record should go to Elastic: `context.execution().emit("elasticsearch", request)`
- else: `consumer.consume(input)` to continue to main sink.
4. Terminate with `syslog` sink.

## Java skeleton

```java
stream.onError().addNamedSink("elasticsearch", ElasticSearchSinkConfiguratorBuilder.builder());

stream.consumeFromSource(NetworkSourceConfigBuilder.<byte[]>builder().withDecoder(Decoders.toByteArrayDecoder()))
      .processWith(bytes -> new String(bytes))
      .processWith(this::route)
      .terminateWithSink(SyslogSinkConfigBuilder.builder());
```

## Runtime config shape

```yaml
source:
  network:
    type: udp
    address: "0.0.0.0:15140"

sink:
  syslog:
    address: "syslog:10514"
  elastic:
    indexName: "logs-index"
    address: "es:9200"
    auth:
      username: "elastic"
      password: "changeme"
    ssl:
      trustStoreFile: "/tmp/cacert"
      insecure: true
```

## Common pitfalls

- Forgetting to expose/bind UDP port when testing in containers.
- Forgetting CA cert bind for TLS Elastic connection.
- Throwing in routing function instead of `handleException(...)` and continuing gracefully.

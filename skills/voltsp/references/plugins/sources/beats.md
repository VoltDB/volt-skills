# Beats Source

Ingest events from Elastic Beats agents (Filebeat, Metricbeat, etc.) over the Lumberjack protocol.

Compile dependency: volt-stream-plugin-beats-api

## Java Example

```java
import org.voltdb.stream.plugin.beats.api.BeatsSourceConfigBuilder;

stream.consumeFromSource(BeatsSourceConfigBuilder.<BeatsMessage>builder()
    .withAddress("0.0.0.0", 5044)
    .withClientInactivityTimeout(Duration.ofSeconds(30))
    .withDecoder(Function.identity())
);
```

## YAML Example

```yaml
source:
  beats:
    address: "0.0.0.0:5044"
    clientInactivityTimeout: "PT30S"
```

## Properties
- HostAndPort address: Listening address in host:port format, required.
- Duration clientInactivityTimeout: Time before closing inactive client connections, default 30s.
- Function&lt;BeatsMessage, T&gt; decoder: Decoder for Beats payloads, required in Java API.

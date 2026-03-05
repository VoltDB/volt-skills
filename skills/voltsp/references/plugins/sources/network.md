# Network Source

Ingest data over UDP or TCP from network endpoints. Supports configurable decoders and OS-level socket options.

Compile dependency: volt-stream-plugin-network-api

## Java Example

```java
import org.voltdb.stream.plugin.network.api.NetworkSourceConfigBuilder;

stream.consumeFromSource(NetworkSourceConfigBuilder.<String>builder()
    .withAddress("0.0.0.0", 34567)
    .withType(NetworkType.UDP)
    .withDecoder(Decoders.toLinesDecoder())
);
```

## YAML Example

```yaml
source:
  network:
    type: udp
    address: "0.0.0.0:34567"
    decoder: "lines"
    socketOptions:
      SO_RCVBUF: "65536"
      SO_TIMEOUT: "1000"
```

## Properties
- HostAndPort address: Server socket binding address, default 0.0.0.0, required.
- NetworkType type: Transport protocol, UDP or TCP, required.
- Decoder&lt;T&gt; decoder: Decoder for received data (e.g. Decoders.toLinesDecoder()), required in Java API.
- Map&lt;String, String&gt; socketOptions: OS socket options (SO_SNDBUF, SO_RCVBUF, SO_TIMEOUT, SO_KEEPALIVE, SO_LINGER, SO_BACKLOG, TCP_NODELAY).

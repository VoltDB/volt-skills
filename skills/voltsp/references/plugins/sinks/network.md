# Network Sink

Send data over UDP or TCP to external consumers. Input type is byte[].

Compile dependency: volt-stream-plugin-network-api

## Java Example

```java
import org.voltdb.stream.plugin.network.api.NetworkSinkConfigBuilder;

stream.terminateWithSink(NetworkSinkConfigBuilder.builder()
    .withType(NetworkType.UDP)
    .withAddressHost("10.11.12.13")
    .withAddressPort(34567)
);
```

## YAML Example

```yaml
sink:
  network:
    type: udp
    address: "10.11.12.13:34567"
```

## Properties
- NetworkType type: Transport protocol, UDP or TCP, required.
- HostAndPort address: Target host and port, required.

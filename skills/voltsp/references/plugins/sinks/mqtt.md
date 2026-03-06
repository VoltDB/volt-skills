# MQTT Sink

Publish events to MQTT topics. Input type is MqttPublishMessage containing topic, QoS level, payload, and message properties. Supports WebSocket transport, OAuth, and TLS.

Compile dependency: volt-stream-plugin-mqtt-api

## Java Example

```java
import org.voltdb.stream.plugin.mqtt.api.MqttSinkConfigBuilder;

stream.terminateWithSink(MqttSinkConfigBuilder.builder()
    .withAddressHost("mqtt.example.com")
    .withAddressPort(1883)
    .withIdentifier("my-publisher")
);
```

## YAML Example

```yaml
sink:
  mqtt:
    address: "mqtt.example.com:1883"
    identifier: "my-publisher"
    auth:
      username: "admin"
      password: "admin"
    websocket:
      subpath: /topic
```

## Properties
- String identifier: MQTT client identifier, auto-generated if not set.
- HostAndPort address: MQTT broker address, default port 1883.
- MqttWebSocketConfig websocket: WebSocket transport configuration (subpath).
- SslConfig ssl: SSL/TLS configuration.
- Credentials auth: Username/password authentication.
- MqttConnectConfig connect: Additional MQTT connect options.
- MqttReconnectConfig reconnect: Automatic reconnect with exponential backoff.
- OAuthConfigurator oauth: OAuth configuration.
- RetryConfiguration retry: Retry configuration for failed publishes.

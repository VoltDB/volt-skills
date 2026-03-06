# MQTT Source

Subscribe to MQTT topics for IoT and event workloads. Supports shared subscriptions, WebSocket transport, OAuth, and TLS.

Compile dependency: volt-stream-plugin-mqtt-api

## Java Example

```java
import org.voltdb.stream.plugin.mqtt.api.MqttSourceConfigBuilder;

stream.consumeFromSource(MqttSourceConfigBuilder.builder()
    .withGroupName("group1")
    .withTopicFilter("sensors/#")
    .withAddressHost("mqtt.example.com")
    .withAddressPort(1883)
    .withQos(MqttMessageQoS.AT_LEAST_ONCE)
);
```

## YAML Example

```yaml
source:
  mqtt:
    address: "mqtt.example.com:1883"
    topicFilter: "sensors/#"
    groupName: "group1"
    qos: "AT_LEAST_ONCE"
    auth:
      username: "admin"
      password: "admin"
```

## Properties
- String identifier: MQTT client identifier, auto-generated with 'voltsp-source-' prefix if not set.
- HostAndPort address: MQTT broker address, default port 1883, required.
- String topicFilter: Topic filter with wildcard support (e.g. "sensors/#"), required.
- String groupName: Shared subscription group name, required.
- MqttMessageQoS qos: Quality of Service level, default AT_LEAST_ONCE.
- MqttWebSocketConfig websocket: WebSocket transport configuration.
- SslConfig ssl: SSL/TLS configuration.
- Credentials auth: Username/password authentication.
- MqttConnectConfig connect: Additional MQTT connect options.
- MqttReconnectConfig reconnect: Automatic reconnect with exponential backoff.
- OAuthConfigurator oauth: OAuth configuration.

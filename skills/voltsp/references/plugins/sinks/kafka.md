# Kafka Sink

Publish processed records to Kafka topics. Supports custom serializers, schema registry, and key/value/header extractors.

Compile dependency: volt-stream-plugin-kafka-api

## Java Example

```java
import org.voltdb.stream.plugin.kafka.api.KafkaSinkConfigBuilder;

stream.terminateWithSink(KafkaSinkConfigBuilder.<String>builder()
    .withBootstrapServers("kafka.example.com:9092")
    .withTopicName("my-topic")
);
```

## YAML Example

```yaml
sink:
  kafka:
    topicName: "my-topic"
    bootstrapServers: "kafka.example.com:9092"
    schemaRegistryUrl: "http://registry.example.com"
    properties:
      acks: "all"
```

## Properties
- List&lt;String&gt; bootstrapServers: Kafka broker addresses, required.
- String topicName: Target Kafka topic, required.
- Map&lt;String, String&gt; properties: Additional Kafka producer properties.
- SslConfig ssl: SSL/TLS configuration.
- Class keySerializer: Key serializer class.
- Class valueSerializer: Value serializer class.
- Function&lt;T, Object&gt; keyExtractor: Extracts the record key from the input element.
- Function&lt;T, Object&gt; valueExtractor: Extracts the record value from the input element.
- Function&lt;T, Iterable&lt;Header&gt;&gt; headerExtractor: Extracts headers from the input element.
- String schemaRegistryUrl: Schema registry URL for Avro/Protobuf serialization.

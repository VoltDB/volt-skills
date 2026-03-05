# Kafka Source

Consume records from Kafka topics with consumer group and offset management.

Compile dependency: volt-stream-plugin-kafka-api

## Java Example

```java
import org.voltdb.stream.plugin.kafka.api.KafkaSourceConfigBuilder;

stream.consumeFromSource(KafkaSourceConfigBuilder.<String>builder()
    .withGroupId("my-group")
    .withTopicNames("topicA", "topicB")
    .withBootstrapServers("serverA:9092", "serverB:9092")
    .withStartingOffset(KafkaStartingOffset.EARLIEST)
    .withPollTimeout(Duration.ofMillis(250))
);
```

## YAML Example

```yaml
source:
  kafka:
    groupId: "my-group"
    bootstrapServers:
      - "serverA:9092"
      - "serverB:9092"
    topicNames:
      - "topicA"
      - "topicB"
    startingOffset: "EARLIEST"
    pollTimeout: "PT0.25S"
    maxCommitTimeout: "PT10S"
    maxCommitRetries: 3
    properties:
      max.poll.interval.ms: "300000"
```

## Properties
- List&lt;String&gt; bootstrapServers: Kafka broker addresses, required.
- Set&lt;String&gt; topicNames: Topics to subscribe to, required.
- String groupId: Consumer group identifier, required.
- KafkaStartingOffset startingOffset: EARLIEST, LATEST, or NONE, default EARLIEST.
- Duration pollTimeout: Max time to block the receiving thread per poll, default 1s.
- Duration maxCommitTimeout: Timeout for commit retries, default 10s.
- int maxCommitRetries: Max retries for committing offsets, default 3.
- int maxPollRecords: Max records returned per poll, default 10000.
- Class keyDeserializer: Key deserializer class, default ByteBufferDeserializer.
- Class valueDeserializer: Value deserializer class, default ByteBufferDeserializer.
- Map&lt;String, String&gt; properties: Additional Kafka consumer properties.
- SslConfig ssl: SSL/TLS configuration.
- String schemaRegistryUrl: Schema registry URL for Avro/Protobuf deserialization.

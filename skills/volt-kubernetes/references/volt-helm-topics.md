# Topics
Topic in VoltDB is a type of exporter. An external client can connect to a topic using standard Kafka client libraries.
Topic is a good candidate for CDC functionality.
Kafka broker service is exposed on a 9092 port.
Example of topics configuration:
```yaml
cluster:
  config:
    deployment:
      # Optional thread pools configuration for exporters
      threadpools:
      - pool:
        name: "topic-pool"
        size: 1
      # Topics configuration for CDC
      topics:
        enabled: true
        threadpool: "topic-pool"
        topic:
        - name: cdc
          format: json
          retention: 1dy
          properties:
            "consumer.skip.internals": false
  serviceSpec:
    kafka:
      type: ClusterIP
      annotations:
        volt: "kafka"
      publicIPFromService: false
```

Important note: Topic names are case-sensitive.

For more information, see [VoltDB Exporters - Topics](https://docs.voltactivedata.com/UsingVoltDB/exporttopics.php).

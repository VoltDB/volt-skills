# Elasticsearch Sink

Index records into Elasticsearch for search and analytics. Supports bulk indexing, load balancing, failover, and SSL/TLS.

Compile dependency: volt-stream-plugin-elastic-api

## Java Example

```java
import org.voltdb.stream.plugin.elastic.api.ElasticSearchSinkConfiguratorBuilder;

stream.terminateWithSink(ElasticSearchSinkConfiguratorBuilder.builder()
    .withIndexName("my-index")
    .withAddressHost("elasticsearch.example.com")
    .withAddressPort(9200)
);
```

## YAML Example

```yaml
sink:
  elastic:
    indexName: "my-index"
    address: "elasticsearch.example.com:9200"
    auth:
      username: "user"
      password: "password"
    ssl:
      trustStoreFile: "/path/to/truststore.jks"
      trustStorePassword: "password"
```

## Properties
- String indexName: Elasticsearch index name, required.
- HostAndPort address: Elasticsearch host and port, default localhost:9200.
- int cacheSizeBytes: Bulk request buffer size in bytes, default 5242880.
- boolean dataStream: Whether to use Elasticsearch data streams, default false.
- RetryConfiguration retry: Retry configuration for failed requests.
- Credentials auth: Username/password authentication credentials.
- SslConfig ssl: SSL/TLS configuration (trustStoreFile, trustStorePassword).
- Map&lt;String, String&gt; requestHeaders: Additional HTTP headers for requests.
- Map&lt;String, String&gt; requestParameters: Additional HTTP query parameters.

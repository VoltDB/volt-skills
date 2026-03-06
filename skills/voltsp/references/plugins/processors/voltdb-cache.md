# VoltDB Cache Processor

Enrich or filter records using VoltDB-backed cache lookups. Caches VoltDB procedure responses keyed by input parameters, with configurable cache size and expiration.

Compile dependency: volt-stream-plugin-volt-api

## Java Example

```java
import org.voltdb.stream.plugin.volt.api.VoltProcedureCacheProcessorConfigBuilder;

stream.processWith(VoltProcedureCacheProcessorConfigBuilder.builder()
    .withVoltClientResource("primary-cluster")
    .withProcedureName("LookupCustomer")
    .withParamsMapper(input -> new Object[]{input.getCustomerId()})
    .withResponseMapper((input, response) -> response.getResults()[0])
    .withComputeFunction((input, cached) -> input.withCustomerName(cached.getString(0)))
    .withMaximumSize(100000)
    .withExpireAfterWrite(Duration.ofMinutes(10))
);
```

## YAML Example

```yaml
processors:
  - voltdb-cache:
      voltClientResource: "primary-cluster"
      procedureName: "LookupCustomer"
      sql: "SELECT name FROM customers WHERE id = ?"
      maximumSize: 100000
      expireAfterWrite: "PT10M"
```

## Properties
- VoltStreamResourceReference voltClientResource: Reference to a VoltDB client resource, required.
- String procedureName: Stored procedure name, default "@AdHoc".
- String sql: SQL query (used with @AdHoc procedure).
- Function&lt;I, Object[]&gt; paramsMapper: Maps input to procedure parameters, required in Java API.
- Function&lt;I, Object&gt; keyMapper: Custom cache key mapper (defaults to paramsMapper output).
- VoltResponseMapperFunction responseMapper: Maps VoltDB response to cached value, required in Java API.
- VoltCachedComputeFunction computeFunction: Computes output from input and cached value, required in Java API.
- int maximumSize: Maximum number of cached entries, default 100000.
- Duration expireAfterWrite: Cache entry expiration time, default 10 minutes.
- RetryConfiguration retry: Retry configuration for failed VoltDB calls.

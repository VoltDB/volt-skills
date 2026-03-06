# VoltDB Procedure Sink

Call VoltDB stored procedures asynchronously for transactional processing. Provides at-least-once delivery semantics. Includes a built-in mapper for Map and VoltProcedureRequest inputs.

Compile dependency: volt-stream-plugin-volt-api

## Java Example

```java
import org.voltdb.stream.plugin.volt.api.VoltSinks;

stream.terminateWithSink(VoltSinks.procedureCall()
    .withVoltClientResource("primary-cluster")
    .withRequestMapper(input -> new VoltProcedureRequest("MyProcedure", input.toArgs()))
);
```

## YAML Example

```yaml
sink:
  voltdb-procedure:
    voltClientResource: "primary-cluster"
```

## Properties
- VoltStreamResourceReference voltClientResource: Reference to a VoltDB client resource, required.
- Function&lt;I, VoltProcedureRequest&gt; requestMapper: Maps input records to procedure call requests.

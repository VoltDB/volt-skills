# CDC Kafka To VoltDB Procedure

## Goal

Consume CDC rows from Kafka, filter for `INSERT`, map to a target procedure call, and apply to a second VoltDB cluster.

## Implementation steps

1. Configure source:
- `source.kafka.topicNames: ["cdc"]`
- earliest offset + string deserializers
2. Parse CDC JSON and map `VOLT_EXPORT_OPERATION` to operation name.
3. Return `null` for non-INSERT events (framework drops nulls).
4. Map to `VoltProcedureRequest` and sink to `voltdb-procedure` with named resource.

## YAML skeleton

```yaml
resources:
  - name: "c2"
    voltdb-client:
      servers: [ "${voltdb.c2.address}" ]

source:
  kafka:
    bootstrapServers: ${kafka.bootstrapServers}
    topicNames: [ "cdc" ]
    groupId: "DR"

processors:
  - javascript:
      script: |
        function process(input) {
          var data = JSON.parse(input.getValue());
          var op = data.VOLT_EXPORT_OPERATION;
          if (op !== 1) { return null; } // INSERT only
          return { procedureName: 'CDC_INSERT', parameters: [data.ORDER_ID, data.CREATED_AT, data.AMOUNT] };
        }

sink:
  voltdb-procedure:
    requestMapper: |
      function process(input) {
        var VoltProcedureRequest = Java.type('org.voltdb.stream.plugin.volt.api.VoltProcedureRequest');
        return new VoltProcedureRequest(input.procedureName, input.parameters);
      }
    voltClientResource: "c2"
```

## Common pitfalls

- Forgetting env values (`kafka.bootstrapServers`, `voltdb.c2.address`).
- Returning plain object to sink without compatible request mapper.

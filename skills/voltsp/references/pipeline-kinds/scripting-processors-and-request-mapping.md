# Scripting Processors And Request Mapping

## Goal

Implement script-driven transforms and Volt procedure request mapping safely.

## Supported styles

1. `javascript` processor returning map compatible with `voltdb-procedure` sink.
2. `javascript` processor returning `VoltProcedureRequest` instance directly.
3. `voltdb-procedure.requestMapper` as JavaScript function.
4. `requestMapper` as Java method reference (`Class::method`) with classes on classpath.
5. `java` and `python` processors for inline script execution.

## YAML example

```yaml
resources:
  - name: voltdb
    voltdb-client:
      servers: ["host-0:21212"]

source:
  collection:
    elements: ["FUNC1"]

processors:
  - javascript:
      script: |
        function process(input) {
          return { procedureName: input, parameters: [3, 4] };
        }

sink:
  voltdb-procedure:
    voltClientResource: "voltdb"
```

## Validation rules from tests

- Script function `process` must have correct argument count.
- JavaScript runtime exceptions are surfaced in logs with script location.
- Java and Python runtime errors are surfaced in logs; assert on message content.

## Common pitfalls

- Wrong function signature (`process(input, tooMany)` etc.).
- Forgetting to mount/load classes required by Java method reference mapping.
- Returning incompatible object shape for sink request mapper.

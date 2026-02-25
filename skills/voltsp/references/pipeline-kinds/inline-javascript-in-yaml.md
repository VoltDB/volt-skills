# Inline JavaScript In YAML Pipelines

## Goal

Use inline JavaScript for event transformation, filtering, and request mapping in YAML pipelines.

## Processor shape

Use `script` for inline code:

```yaml
processors:
  - javascript:
      script: |
        function process(input) {
          if (input == null) {
            return null;
          }
          return String(input).toUpperCase();
        }
```

Use `scriptUrl` for deterministic reusable scripts:

```yaml
processors:
  - javascript:
      scriptUrl: "classpath:/scripts/transform.js"
```

`script` or `scriptUrl` is required.

## Volt request mapping patterns

Processor returns map compatible with `voltdb-procedure` sink:

```yaml
processors:
  - javascript:
      script: |
        function process(input) {
          return {
            procedureName: input,
            parameters: [3, 4]
          };
        }
```

Custom JS `requestMapper` in sink/emitter:

```yaml
sink:
  voltdb-procedure:
    requestMapper: |
      function process(input) {
        var VoltProcedureRequest = Java.type('org.voltdb.stream.plugin.volt.api.VoltProcedureRequest');
        return new VoltProcedureRequest(input.procedureName, input.parameters);
      }
```

For function-like YAML fields (`requestMapper`, `computeFunction`, etc.), non-`Class::method` values are evaluated as JavaScript.

## Function contracts

- Define a callable `process` function.
- Regular function fields expect one argument: `process(input)`.
- Bi-function fields (for example emitter `computeFunction`) expect two arguments: `process(input, results)`.
- Wrong arity fails startup with an explicit error (`Expected: X, actual: Y`).

## Runtime behavior and troubleshooting

- Returning `null` drops the record.
- Runtime JS exceptions are rethrown as `JavaScript execution error in script: ...`.
- Logs include guest stack frames and the offending source line, which is useful for fast diagnosis.

## Common pitfalls

- Defining `map(...)` instead of `process(...)`.
- Returning an incompatible object for `voltdb-procedure` mapping.
- Using undocumented fields from stale snippets (for example `timeoutMs` in old sample YAML).

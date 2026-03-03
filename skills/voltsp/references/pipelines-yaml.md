# Pipelines (YAML API)

Use this when defining the full pipeline declaratively.

## Required structure

Use this as the baseline shape:

```yaml
$schema: "https://docs.voltdb.com/ActiveSP/schemas/voltsp1.6.0.json"
version: 1
name: "stdin-to-stdout"
source: {}
processors: []
sink: {}
```

Rules:

- `version` must be `1`.
- `name`, `source`, and `sink` are required.
- `processors`, `resources`, and `logging` are optional.
- Prefer `$schema` for IDE autocomplete and validation.

## Definition vs runtime config

Do not mix these concepts:

- Pipeline definition YAML: structure and operator graph (`source`, `processors`, `sink`, `resources`, `logging`).
- Runtime configuration YAML: environment values consumed by operators/builders or `configurator().findByPath(...)`.

Use `scripts/check_voltsp_yaml_layout.py` to catch this mix-up early.

## Function-valued fields

When an operator expects a function, choose one of:

- Java method reference: `com.example.Factory::mapEvent`
- Inline script (JavaScript/Python): code block under field value

For Java method references:

- Keep the target method public and unambiguous.
- Avoid overloaded names for method references.
- Ensure classes are present on classpath at startup.

## Resources and logging

- Define reusable clients under `resources` and reference them by name in operators.
- Use `logging.globalLevel` and `logging.loggers` for runtime log tuning.
- Remember YAML logging config applies after startup; startup-time logging may still require CLI/Helm logging settings.

## Common startup failures

- Class not found for method references: classpath or FQCN issue.
- Ambiguous method name: overloaded method reference.
- Invalid YAML type for operator field: schema mismatch.
- Missing required section (`name`, `source`, `sink`) or invalid `version`.

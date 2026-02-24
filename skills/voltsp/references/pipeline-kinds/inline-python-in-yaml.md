# Inline Python In YAML Pipelines

## Goal

Use Python code in YAML pipelines when transformation logic is easier to express in Python.

## Processor shape

Inline script:

```yaml
processors:
  - python:
      script: |
        def process(input):
          if isinstance(input, str):
            return input.upper()
          return input
```

Script from URI:

```yaml
processors:
  - python:
      scriptUrl: "classpath:/scripts/transform.py"
```

`script` or `scriptUrl` is required.

## Function contract

- Define `def process(input): ...`.
- Return transformed value for downstream operators.
- Return `None` to drop a record.

## Config fields from record docs

- `script`: Python code to execute.
- `scriptUrl`: URI to Python file.
- `timeout`: duration field with default `1s` in config metadata.

For `timeout`, verify behavior against your runtime version before relying on it for hard execution limits.

## Runtime behavior and troubleshooting

- Runtime failures are wrapped as `Python execution error in script: ...`.
- Typical messages surface guest-language causes (for example `AttributeError`).
- As with JS, guest stack/source context is attached when available.

## Common pitfalls

- Forgetting to define `process`.
- Returning incompatible types for downstream sinks/processors.

# ONNX GenAI Processor (Processor)

## Purpose

Run GenAI-style ONNX workflows for prompt/response transformations.

Compile dependency:

- org.voltdb:volt-stream-plugin-onnx-api

## When To Use

- Transform, enrich, or filter records between source and sink.
- Externalize model/script/class parameters through runtime config.

## When To Avoid

- Avoid if a plain Java lambda/function is simpler and more maintainable.
- Avoid embedding large scripts/models inline when they should be versioned assets.

## Java Example

```java
stream.processWith(
    /* Use ONNX GenAI Processor builder/configurator for 'onnx-genai' */
);
```

## YAML Example

```yaml
processors:
  - onnx-genai:
      # plugin-specific fields
```

## Runtime Config Keys

- Pipeline-definition path: `processors[].onnx-genai`
- Helm auto-config path: `streaming.pipeline.configuration.processors.onnx-genai`
- Keep secrets in secure config overlays.

## Helm Notes

- Keep model/script/class values configurable by environment.
- Check CPU/memory requirements for heavy processor workloads.

## Testing Checks

- Unit-test transformation behavior with deterministic fixtures.
- Add integration checks around plugin runtime requirements.
- Verify null/filter semantics where processor intentionally drops events.

## Common Failures

- Invalid processor-specific field types in YAML.
- Missing runtime dependencies for script/model execution.
- Model/chat template/token settings exceed resource limits or produce invalid output.

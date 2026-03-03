# ONNX GenAI Local Model Pipeline

## Goal

Run local ONNX GenAI inference from a mounted model directory and stream response tokens to stdout.

## Implementation steps

1. Use `source.collection` with prompt strings.
2. Configure `onnx-genai` processor:
- `modelUri`
- `chatTemplate`
- `streamResponse`
- optional `properties` (e.g. `max_length`)
3. Terminate with `stdout`.
4. In containerized tests, bind/mount the model path read-only.

## YAML skeleton

```yaml
source:
  collection:
    elements:
      - "Tell me a short joke starting with word Doctor."

processors:
  - onnx-genai:
      modelUri: "file:///tmp/Phi-4-mini-instruct-onnx/cpu-int4-rtn-block-32-acc-level-4"
      printDownloadProgress: true
      chatTemplate: "<|user|>\n{input} <|end|>\n<|assistant|>"
      streamResponse: true
      properties:
        max_length: "32"

sink:
  stdout: {}
```

## Common pitfalls

- Incorrect `modelUri` path inside container.
- Missing chat template placeholder (`{input}`).
- Not accounting for token-streamed output when asserting logs.

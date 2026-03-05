# ONNX GenAI Processor

Run generative AI inference using ONNX models with chat template support. Supports token-by-token streaming and configurable generation parameters.

Compile dependency: volt-stream-plugin-onnx-api

## Java Example

```java
import org.voltdb.stream.plugin.onnx.api.OnnxGenaiProcessorConfigBuilder;

stream.processWith(OnnxGenaiProcessorConfigBuilder.builder()
    .withModelUri("s3-models-storage://com.acme.chatmodels/phi4-mini-instruct")
    .withChatTemplate("<|user|>\\n{input} <|end|>\\n<|assistant|>")
    .withStreamResponse(true)
);
```

## YAML Example

```yaml
processors:
  - onnx-genai:
      modelUri: "s3-models-storage://com.acme.chatmodels/phi4-mini-instruct"
      chatTemplate: "<|user|>\\n{input} <|end|>\\n<|assistant|>"
      printDownloadProgress: true
      streamResponse: true
      properties:
        max_length: "2048"
        temperature: "0.7"
      cache:
        directory: "/media/"
```

## Properties
- VoltStreamResourceReference modelResource: Reference to a managed model resource.
- URI modelUri: Direct URI to an ONNX GenAI model.
- String chatTemplate: Chat template with {input} placeholder for prompt formatting.
- Boolean streamResponse: Enable token-by-token streaming output.
- Boolean printDownloadProgress: Show download progress when fetching remote models.
- Map&lt;String, String&gt; properties: Model-specific generation parameters (max_length, temperature, etc.).
- FileCacheConfig cache: Local file cache configuration for remote models (directory).

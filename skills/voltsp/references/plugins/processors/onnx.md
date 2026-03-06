# ONNX Processor

Apply ONNX model inference for ML scoring in-stream. Supports model loading from URIs or managed resources (e.g. MLflow), with configurable tensor names and session options. Supports hot-reload of models.

Compile dependency: volt-stream-plugin-onnx-api

## Java Example

```java
import org.voltdb.stream.plugin.onnx.api.OnnxProcessorConfigBuilder;

stream.processWith(OnnxProcessorConfigBuilder.builder()
    .withModelUri("file:///path/to/model.onnx")
    .withInputTensorName("float_input")
    .withOutputTensorNames("output_label", "output_probability")
);
```

## YAML Example

Using a direct model URI:

```yaml
processors:
  - onnx:
      modelUri: "file:///path/to/model.onnx"
      inputTensorName: "float_input"
      outputTensorNames:
        - "output_label"
        - "output_probability"
```

Using a managed model resource (e.g. MLflow):

```yaml
resources:
  - name: "mlflow-model"
    mlflow-model:
      trackingUri: "http://mlflow:5000"
      modelName: "my-classifier"
      pollInterval: "PT5S"

processors:
  - onnx:
      modelResource: "mlflow-model"
      inputTensorName: "float_input"
      outputTensorNames:
        - "output_label"
        - "output_probability"
```

## Properties
- VoltStreamResourceReference modelResource: Reference to a managed model resource (e.g. MLflow).
- URI modelUri: Direct URI to an ONNX model file.
- String inputTensorName: Name of the input tensor, required.
- List&lt;String&gt; outputTensorNames: Names of output tensors to retrieve.
- Boolean printDownloadProgress: Show download progress when fetching remote models.
- FileCacheConfig cache: Local file cache configuration for remote models.
- OrtSessionOptions sessionOptions: ONNX Runtime session options.

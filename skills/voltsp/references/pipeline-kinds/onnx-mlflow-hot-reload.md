# ONNX MLflow Hot Reload Pipeline

## Goal

Load model versions from MLflow and refresh in running pipeline by polling model registry.

## Implementation steps

1. Configure `mlflow-model` resource with `trackingUri`, `modelName`, `pollInterval`.
2. Use `onnx` processor with `modelResource` and tensor names.
3. Keep inference source deterministic (`generate` + fixed request generator).
4. In tests, run MLflow container with stable network alias (e.g. `mlflow`).

## YAML skeleton

```yaml
source:
  generate:
    tps: 1
    generator: "org.voltdb.stream.e2e.onnx.SomeInferenceRequest::preset"

resources:
  - name: "mlflow-model"
    mlflow-model:
      trackingUri: "http://mlflow:5000"
      modelName: "my-classifier"
      pollInterval: 5s

processors:
  - onnx:
      modelResource: "mlflow-model"
      inputTensorName: "float_input"
      outputTensorNames: ["output_label", "output_probability"]
  - javascript:
      script: |
        function process(input) { return input.toString(); }

sink:
  stdout: {}
```

## Common pitfalls

- Wrong model name in MLflow resource config.
- Missing network route from VoltSP container to MLflow endpoint.
- Poll interval too long for tests expecting quick hot reload.

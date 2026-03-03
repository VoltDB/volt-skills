# Pipeline Kinds (From E2E Tests)

Use this index when asked to implement a specific pipeline shape from validated reference patterns in this skill.

## Routing

- Network ingest with conditional routing: `references/pipeline-kinds/network-to-syslog-with-elastic-side-route.md`
- Two-stage bridge (Network -> Volt topic -> Kafka/Syslog/Elastic): `references/pipeline-kinds/network-to-volt-topic-bridge.md`
- CDC replication (Kafka export -> Volt procedure): `references/pipeline-kinds/cdc-kafka-to-voltdb-procedure.md`
- Rate-limited synthetic generator: `references/pipeline-kinds/rate-limited-generator.md`
- ONNX GenAI local model inference: `references/pipeline-kinds/onnx-genai-local-model.md`
- ONNX model via MLflow hot reload: `references/pipeline-kinds/onnx-mlflow-hot-reload.md`
- Scripting processors and Volt request mapping: `references/pipeline-kinds/scripting-processors-and-request-mapping.md`
- Pipeline logging configuration: `references/pipeline-kinds/logging-configuration.md`

## Inline Scripting

- Inline JavaScript in YAML: `references/pipeline-kinds/inline-javascript-in-yaml.md`
- Inline Python in YAML: `references/pipeline-kinds/inline-python-in-yaml.md`
- Inline Java in YAML: `references/pipeline-kinds/inline-java-in-yaml.md`

## Usage rule

- Pick one pattern file first.
- Reuse its config paths and operator order before introducing new operators.
- Keep environment-specific addresses and credentials in runtime config/Helm values.

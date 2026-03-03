# Pipelines (YAML-defined)

Scope: public-candidate (pipeline authoring + how to run).

## Use the canonical docs first

- YAML pipeline format + schema: `volt-stream-docs/docs/yaml.md`

## Remember the two kinds of “YAML” in VoltSP

- **Pipeline definition YAML**: describes the full pipeline (`version`, `name`, `source`, `processors`, `sink`, `resources`, `logging`, ...).
- **Configuration YAML** (CLI `--config` / Helm values): provides runtime properties for pipelines/templates and interpolation.

## Run a YAML-defined pipeline with the CLI

- Pass the pipeline definition as the positional argument:
  - `voltsp -l /path/to/license.xml path/to/pipeline.yaml`
- Implementation detail (useful for debugging):
  - VoltSP detects `.yaml`/`.yml`, sets `-Dvoltsp.pipeline.definitionFile=<abs-path>`, and runs `org.voltdb.stream.config.yaml.YamlConfiguredPipeline`.
  - See `volt-stream-core/src/main/java/org/voltdb/stream/execution/PipelineConfigurationHelper.java`.

## Get IDE validation/autocomplete

- Reference the JSON schema with `"$schema"` as documented in `volt-stream-docs/docs/yaml.md`.

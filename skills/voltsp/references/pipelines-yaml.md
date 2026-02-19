# Pipelines (YAML-defined)

Use this when you want to define the whole pipeline declaratively, without writing Java.

## Pipeline definition vs runtime configuration

- **Pipeline definition YAML** describes the pipeline (`version`, `name`, `source`, `processors`, `sink`, `resources`, `logging`, ...).
- **Runtime configuration YAML** (CLI `--config` / Helm values) provides environment-specific properties and secrets.

## Minimal pipeline example

```yaml
$schema: "https://docs.voltdb.com/ActiveSP/schemas/voltsp<version>.json"
version: 1
name: "stdin-to-stdout"

source:
  stdin: {}

processors:
  - javascript:
      script: |
        function process(input) {
          return input;
        }

sink:
  stdout: {}
```

Notes:

- Set `<version>` to your VoltSP release (or just rely on IDE schema association).
- Use `$schema` to get autocomplete and validation in your editor.

## Run with the CLI

- `voltsp -l /path/to/license.xml path/to/pipeline.yaml`
- Add runtime config when needed (varies by version): `--config path/to/config.yaml`

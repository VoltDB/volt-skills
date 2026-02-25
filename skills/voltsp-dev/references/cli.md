# CLI (`voltsp`)

Scope: public-candidate (how to run locally / bare metal).

## Use the canonical docs first

- CLI usage + env vars: `volt-stream-docs/docs/commandline.md`

## Understand the main input modes

- Run a **Java pipeline class** (pipeline code must be on the classpath):
  - `voltsp -l /path/to/license.xml com.acme.MyPipeline`
- Run a **YAML-defined pipeline** (pipeline definition file is the positional argument):
  - `voltsp -l /path/to/license.xml /path/to/pipeline.yaml`
- Provide runtime configuration:
  - `--config /path/to/config.yaml`
  - `--configSecure /path/to/configSecure.yaml` (values are treated as secrets and not logged)

## Source of truth for flags

- See `volt-stream-cli/src/main/java/org/voltdb/stream/execution/cli/VoltSpCommand.java`.

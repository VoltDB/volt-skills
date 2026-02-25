# Repo map (volt-stream / VoltSP)

Scope: internal (repo navigation for contributors).

## Start with existing docs

- Build + prerequisites + internal Maven settings: `README.md` (and `etc/settings.internal.xml`)
- Product docs index: `volt-stream-docs/docs/intro.md`

## Maven modules (high level)

- Public pipeline DSL (Java): `volt-stream-api/`
- YAML-defined pipelines: `volt-stream-yaml-api/`
- Runtime engine / execution: `volt-stream-core/` (entry point: `org.voltdb.stream.execution.Main`)
- CLI (`voltsp`): `volt-stream-cli/` (entry point: `org.voltdb.stream.execution.cli.VoltSpCommand`)
- Built-in connectors/operators:
  - API: `volt-stream-connectors-api/`
  - Implementations + tests: `volt-stream-connectors-core/`
- Plugins (separate Maven modules): `plugins/`
- Plugin build/codegen infrastructure: `volt-stream-plugin-infrastructure/` and `volt-stream-maven-*/`
- Helm / Kubernetes:
  - Main chart(s): `volt-stream-chart/`
  - Operator: `volt-stream-kubernetes-operator/`
- Docker packaging: `volt-stream-docker/`
- Documentation sources/build: `volt-stream-docs/` (MkDocs sources under `docs/`, generated output under `target/`)
- Testing tooling:
  - Test utilities/examples: `volt-stream-test/`
  - JUnit 5 + Testcontainers extension: `volt-stream-junit-extension/` (`StreamEnvExtension`)
  - Testcontainers wrapper for running VoltSP: `volt-stream-testcontainer/` (see `volt-stream-docs/docs/building-testing-and-deploying.md` for examples)
  - End-to-end tests: `volt-stream-e2e-tests/`

## Key runtime behaviors to remember

- If the CLI positional argument is a `.yaml`/`.yml` file, VoltSP sets `-Dvoltsp.pipeline.definitionFile=<abs-path>` and runs `org.voltdb.stream.config.yaml.YamlConfiguredPipeline` (see `volt-stream-core/src/main/java/org/voltdb/stream/execution/PipelineConfigurationHelper.java`).

## Where to look for examples

- Pipeline examples: `volt-stream-examples/` and `examples/`
- Pipeline tests: `volt-stream-test/src/test/java/`
- Plugin examples + tests: `plugins/*/src/test/java/`
- E2E tests: `volt-stream-e2e-tests/src/test/java/`

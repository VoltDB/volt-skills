# Pipelines (Java DSL)

Scope: public-candidate (pipeline authoring patterns + pointers).

## Use the canonical docs first

- Java DSL overview + patterns: `volt-stream-docs/docs/develop.md`
- Configuration patterns (CLI/Docker/Helm): `volt-stream-docs/docs/configuring-pipeline.md`
- Packaging + local testcontainers-based testing: `volt-stream-docs/docs/building-testing-and-deploying.md`
- Custom operators (extension API): `volt-stream-docs/docs/customoperators.md`

## Start from a template

- Generate a starter project from the Maven archetype (see `volt-stream-docs/docs/quickstart/kubernetes.md` or `volt-stream-docs/docs/building-testing-and-deploying.md`).
- Keep pipeline code in `src/main/java/...` and Helm/config YAML in `src/main/resources/...`.

## Follow the DSL shape

- Implement `org.voltdb.stream.api.pipeline.VoltPipeline`.
- Define the stream as: `consumeFromSource(...) -> processWith(...) -> terminateWithSink(...)`.

## Externalize runtime settings

- Read runtime settings from `ExecutionContext.ConfigurationContext` (see examples in `volt-stream-docs/docs/develop.md` and `volt-stream-docs/docs/configuring-pipeline.md`).
- Keep environment-specific values (hosts, ports, topics, credentials) out of code:
  - Use `--config` / `--configSecure` with the CLI
  - Or Helm values under `streaming.pipeline.configuration*` (see `volt-stream-docs/docs/confighelm.md`)

## Choose “inline operator” vs “plugin”

- Inline (in the pipeline JAR) is fine for one-off logic.
- Prefer a reusable plugin when:
  - Multiple pipelines need the same operator
  - You want generated builders + docs from config records
  - You want to ship implementation separately from pipeline code
- See `references/plugins.md` for the plugin workflow.

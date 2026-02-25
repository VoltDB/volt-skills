# Plugins (sources/sinks/processors/resources/emitters)

Scope: mixed (mostly public-candidate patterns; repo-specific layout is internal).

## Use the existing plugin guides first

- Repo plugin “prompt” guide: `references/plugins/developing_plugins_llm.md`
- Concrete examples:
  - `plugins/network/`
  - `plugins/beats/`
  - `plugins/onnx/`
  - `plugins/mlflow/`

## Follow the repo conventions

- Create a Maven module under `plugins/<name>/` and add it to `plugins/pom.xml`.
- Define a config `record` in `org.voltdb.stream.plugin.<name>.api` and annotate it with `@VoltSP.{Source|Sink|Processor|Resource|Emitter}` + `@Field(...)`.
- Implement the operator in `org.voltdb.stream.plugin.<name>` with a public constructor `(Logger, <ConfigRecord>)`.

## Common “gotchas” worth remembering

- Ensure the plugin module is wired with the VoltSP Maven plugin so `*ConfigBuilder` types are generated.
- Prefer `ExecutionContext.configurator().configureOnce(...)` for expensive shared fixtures.
- Default exception handler: use `config.exceptionHandler()` when present, otherwise fall back to `context.execution()::handleException`.

## Lean on generated builders + docs

- Ensure the plugin module uses the VoltSP Maven plugin so the `*ConfigBuilder` is generated.
- Run `mvn clean install` to generate builders and validate defaults.

## Test at the right level

- Unit/in-process simulation: use `MainSimulator` / `MainSimulation` patterns from `plugins/*/src/test/java`.
- Integration/E2E: use `VoltSpContainer` + `StreamEnvExtension` + Testcontainers (see `references/testing.md`).

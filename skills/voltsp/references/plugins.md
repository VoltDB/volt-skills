# Plugins (sources/sinks/processors/resources/emitters)

Use this as a quick “how to structure a plugin” index + checklist.

## Module layout

- A plugin is usually a separate Maven module that produces a JAR consumed by VoltSP.
- If you are working inside the VoltSP source repo, plugins typically live under `plugins/<name>/` and are added to the parent `plugins/pom.xml`.

## Minimal implementation checklist

- Define a config `record` in `org.voltdb.stream.plugin.<name>.api` and annotate it with `@VoltSP.{Source|Sink|Processor|Resource|Emitter}` + `@Field(...)`.
- Implement the operator in `org.voltdb.stream.plugin.<name>` with a public constructor `(Logger, <ConfigRecord>)`.
- Build the module so the `*ConfigBuilder` types (if your build generates them) are created and defaults are validated.

Minimal config record shape:

```java
@VoltSP.Source(name = "my-source", implementation = "org.acme.MySource")
public record MySourceConfig(
  @Field(description = "Address to bind", required = true) HostAndPort address
) {}
```

## Useful patterns

- Prefer `ExecutionContext.configurator().configureOnce(...)` for expensive shared fixtures.
- Default exception handler: use `config.exceptionHandler()` when present, otherwise fall back to `context.execution()::handleException`.

## Testing

- Use `MainSimulator`/`MainSimulation` for in-process simulations and `StreamEnvExtension` + Testcontainers for integration tests.
- Prefer `Awaitility.await()` over `Thread.sleep()`.

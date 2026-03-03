# Testing (pipelines + plugins)

Scope: mixed (public-candidate patterns + repo-specific utilities).

## Use the canonical docs first

- Local testing + deployment packaging patterns: `volt-stream-docs/docs/building-testing-and-deploying.md`
- Testcontainers/JUnit extension details: `volt-stream-junit-extension/README.md`
- Repo root notes on integration tests: `README.md` (section “Writing integration tests”)

## Know the main test styles

- Unit tests: pure JUnit 5, no containers (fastest).
- Integration tests: Kafka/Schema Registry/VoltDB via Testcontainers.
- E2E tests: run VoltSP in a container (`VoltSpContainer`) and assert from logs/outputs.

## Use StreamEnvExtension for container orchestration

- Use `@ExtendWith(StreamEnvExtension.class)` and request containers by name with `@NamedContainer`.
- Use `@ConfigureOnce` / `@CleanOnce` to set up expensive fixtures once per test class.
- Prefer `Awaitility.await()` over `Thread.sleep()`.

## Preferred operator test pattern (repo convention)

- For sinks/sources/processors/resources, prefer:
  1) a small `VoltPipeline` that wires the operator under test and collects outputs (for example via an in-memory sink)
  2) a test that runs it via `MainSimulator.fork(LocalConfiguration)` and asserts via `Awaitility`

Minimal skeleton to copy (adapt to your plugin/operator):

- Pipeline under test: implement `VoltPipeline` and collect outputs (for example via a `MemorySink`).
- Test harness:
  - create `LocalConfiguration` via `forSimulation()`
  - run with `MainSimulator.fork(configuration)`
  - assert readiness and results with `Awaitility.await().untilAsserted(...)`
  - tear down with `simulation.exit(Duration.ofSeconds(10))` in `@AfterEach`

## Where to copy patterns from

- Pipeline integration tests: `volt-stream-test/src/test/java`
- Plugin tests: `plugins/*/src/test/java`
- E2E tests: `volt-stream-e2e-tests/src/test/java`

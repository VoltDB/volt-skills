# Testing (pipelines + plugins)

Use this to pick the right test level and common patterns.
For concrete implementation shapes derived from e2e tests, read `references/pipeline-kinds.md`.

## Choose the test level

- Use unit tests for pure logic and mapping functions.
- Use in-process simulation (if available) for pipeline behavior without container overhead.
- Use Testcontainers for integration boundaries (Kafka, Schema Registry, VoltDB, real VoltSP image).
- Use black-box container tests before release when runtime wiring matters (classpath, config files, license, worker count).

## Async testing rules

- Prefer `Awaitility.await()` over fixed sleeps.
- Assert on observable outcomes (logs, sink output, side effects), not internal timing.
- Keep timeouts explicit and short for developer feedback.

## Black-box pattern (VoltSpContainer style)

Use a container test to validate runtime behavior end to end:

- Set license path explicitly.
- Mount app JAR/classes explicitly.
- Pass configuration YAML explicitly.
- Set parallelism explicitly (`withParallelism(...)`).
- Wait for startup and assert emitted output.

## Plugin/operator-specific tests

- Test config records/builders directly in unit tests.
- Replace remote dependencies with deterministic test doubles where possible.
- Verify commit behavior and retries for custom source/sink operators.
- Add one parallelism-focused test when operator touches shared resources (files, sockets, caches).

## Deterministic test inputs

- Keep test fixtures in static files under source control.
- Keep random generators seeded in test scenarios.
- Use fixed topic names, host aliases, and test paths to avoid flaky assertions.

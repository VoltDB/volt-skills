# Testing (pipelines + plugins)

Use this to pick the right test level and common patterns.

## Choose the test level

Guidelines:

- Prefer `Awaitility.await()` for async assertions; avoid unconditional sleeps.
- For operator tests, prefer an in-process simulation when possible; use containers for integration boundaries (Kafka/Schema Registry/VoltDB) or full black-box runs.

Common building blocks:

- **Unit tests**: pure JUnit 5 for small logic (fastest).
- **In-process simulation** (if available in your SDK): `MainSimulator` / `MainSimulation` running a small `VoltPipeline` and collecting outputs.
- **Integration tests**: Testcontainers for Kafka/Schema Registry/VoltDB plus a small pipeline under test.
- **Black-box tests**: run the real VoltSP image in Testcontainers (for example with a VoltSP-specific `VoltSpContainer` wrapper, if your SDK provides it).

## Container orchestration with JUnit (if your SDK provides it)

Some VoltSP SDKs ship a JUnit 5 extension that provisions named containers (Kafka, Schema Registry, etc.).

Common pattern:

- annotate test with `@ExtendWith(StreamEnvExtension.class)`
- inject containers via `@NamedContainer(...)`
- use `@ConfigureOnce` / `@CleanOnce` for expensive fixtures configured once per class

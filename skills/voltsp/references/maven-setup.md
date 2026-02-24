# Maven Setup For Java Pipelines

Use this when creating a Java DSL pipeline project that compiles against VoltSP artifacts published to Maven Central.

## Goal

Set up Maven so:
- pipeline code compiles locally,
- runtime-provided VoltSP classes are not bundled unnecessarily,
- tests can run with VoltSP test tooling.

## Required dependencies

For a minimal Java pipeline project, include:
- `org.voltdb:volt-stream-api`
- `org.voltdb:volt-stream-connectors-api`

Use `provided` scope for VoltSP/runtime-provided libraries in most deployments.

## Common optional dependencies

Add only when needed by your pipeline:
- Volt procedure sink/emitter APIs: `org.voltdb:volt-stream-plugin-volt-api` (`provided`)
- Kafka source/sink APIs: `org.voltdb:volt-stream-plugin-kafka-api` (`provided`)
- VoltDB Java client: `org.voltdb:voltdbclient` (`provided`)
- Kafka clients: `org.apache.kafka:kafka-clients` (`provided`)

Test stack:
- `org.voltdb:volt-stream-testcontainer` (`test`)
- `org.voltdb:volt-stream-api-test` (`test`)
- JUnit + AssertJ (`test`)

## Scope rules

- `provided`: class is needed for compile, supplied by runtime image/platform.
- `compile`: class must be packaged with your app artifact.
- `test`: only for tests.

If your runtime does not provide a dependency, move it from `provided` to `compile` and package it.

## Template POM

Use template:
- `assets/templates/maven/pom.xml`

Copy it as the project `pom.xml`, then update:
- `groupId`
- `artifactId`
- `version`
- `volt.stream.version`
- optional dependency blocks based on chosen plugins

## Validation commands

```bash
mvn -q -DskipTests compile
mvn -q test
mvn -q dependency:tree
```

If compilation fails with missing classes, check:
- dependency present in `pom.xml`,
- correct scope,
- `volt.stream.version` aligned with your runtime version.

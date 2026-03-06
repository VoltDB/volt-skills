# Maven Setup For Java Pipelines

Use this when creating a Java DSL pipeline project that compiles against VoltSP artifacts published to Maven Central.

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

## Template POM

Use template:
- `assets/templates/maven/pom.xml`

Copy it as the project `pom.xml`, then update:
- `groupId`
- `artifactId`
- `version`
- `volt.stream.version`
- optional dependency blocks based on chosen plugins

If compilation fails with missing classes, check:
- dependency present in `pom.xml`,
- correct scope,
- `volt.stream.version` aligned with your runtime version.

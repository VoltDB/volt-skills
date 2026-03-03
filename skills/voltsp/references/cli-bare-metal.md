# CLI (`voltsp`)

Use this when running VoltSP on a workstation/VM (“bare metal”).

## Preflight

- Confirm Java 21+ is available.
- Confirm a valid VoltSP license file is available.
- Confirm `voltsp --help` works for the installed version.

If `-l` is omitted, VoltSP searches for `license.xml` in:

1. user home directory
2. system temp directory
3. installation directory

## Verify environment quickly

```shell
voltsp -l /path/to/license.xml org.volt.stream.test.pipeline.VerifyEnvironment
```

Expected output includes environment checks such as license and Java validation.

## Run a Java pipeline class

1. Put your app JAR (and non-provided dependencies) on classpath:

- `export CP=/path/to/your-pipeline.jar`
- Or: `export CP=/path/to/lib/*:/path/to/your-pipeline.jar`

2. Run pipeline:

- `voltsp com.acme.MyPipeline`

## Run a YAML-defined pipeline

- `voltsp path/to/pipeline.yaml`

## Supply runtime configuration

Pass value files as needed:

- `--config path/to/config.yaml`
- `--configSecure path/to/configSecure.yaml` (secrets; not logged)

Read interpolation and secure-value rules in `references/configuration.md`.

## Useful environment variables

- `JAVA_HOME` / `JAVA_OPTS`
- `CP` (extra classpath entries)
- `HEAP_PCT` or `HEAP_SIZE`
- `LOG4J_PATH`

## Troubleshooting checklist

- If classes aren’t found, re-check `CP` and your JAR contents.
- If process exits early, rerun with `--debug` and inspect startup logs.
- If config values are ignored, verify exact `findByPath(...)` path and check for DSL override of same property.

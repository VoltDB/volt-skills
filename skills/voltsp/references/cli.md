# CLI (`voltsp`)

Use this when running VoltSP on a workstation/VM (“bare metal”).

## Quick start

- See flags for *your* version: `voltsp --help`
- Requirements: Java 21+ and a valid VoltSP license file.

## Run a Java pipeline class

1) Build your pipeline JAR:

- `mvn clean package`

2) Put your JAR (and optional deps) on the classpath (recommended):

- `export CP=/path/to/your-pipeline.jar`
- Or: `export CP=/path/to/lib/*:/path/to/your-pipeline.jar`

3) Run:

- `voltsp -l /path/to/license.xml com.acme.MyPipeline`

## Run a YAML-defined pipeline

- `voltsp -l /path/to/license.xml path/to/pipeline.yaml`

## Runtime configuration (version-dependent)

Most distributions support passing runtime YAML config:

- `--config path/to/config.yaml` (sometimes `-c path/to/config.yaml`)
- `--configSecure path/to/configSecure.yaml` (secrets; not logged)

## Useful environment variables

- `JAVA_HOME` / `JAVA_OPTS`
- `CP` (extra classpath entries)
- `HEAP_PCT` or `HEAP_SIZE`

## Troubleshooting checklist

- If classes aren’t found, re-check `CP` and your built JAR.
- If it exits immediately, rerun with additional logging in `JAVA_OPTS` and inspect output.

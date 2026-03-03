# Runtime Configuration Model

Use this when deciding where configuration belongs and how values are resolved.

## Separate definition from configuration

- Pipeline definition (Java DSL or YAML API): pipeline topology and operators.
- Runtime configuration: environment-specific values, credentials, and deploy-time overrides.

Do not copy `source/processors/sink` graph into runtime config files.

## Where to pass runtime values

- Bare metal CLI:
  - `-c` / `--config` for standard values
  - `-cs` / `--configSecure` for sensitive values
  - `--system-property KEY=value` for specific overrides
- Docker: same flags, typically mounted at `/etc/voltsp/configuration.yaml` and `/etc/voltsp/configurationSecure.yaml`.
- Helm:
  - `streaming.pipeline.configuration`
  - `streaming.pipeline.configurationSecure`
  - `streaming.javaProperties`

## Read values in Java pipelines

Read values through configurator paths:

```java
var config = stream.getExecutionContext().configurator();
int tps = config.findByPath("generator.tps").orElse(10);
```

Use defaults for optional values and fail fast for required values.

## Interpolation

Supported patterns:

- Environment: `${env:VAR}` or `${env:VAR:DEFAULT}`
- System property: `${VAR}` or `${VAR:DEFAULT}`
- Secret wrappers:
  - `${secret:env:VAR}`
  - `${secret:VAR:DEFAULT}`
- AWS secrets:
  - `${aws:secret-name:default}`
  - `${secret:aws:secret-name:}`
- Escape interpolation literal: `${{ raw ${text} }}`

Notes:

- Secret values are protected from logging.
- Secret patterns cannot be composed with prefix/suffix interpolation.
- AWS secret manager can use default chain or explicit environment variables.

## Precedence and mixed style

- Combine auto-configured operator values with Java DSL overrides when needed.
- If same property is set in both runtime config and Java DSL, Java DSL value wins.
- Keep complex object construction in code and simple scalar values in runtime config.

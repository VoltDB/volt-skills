# Canonical Versions

> **Single source of truth for VoltDB and toolchain versions referenced by this skill.**
> When bumping a version, edit ONLY this file. Every template in the other rule files uses placeholders that the agent substitutes from the table below.

## Versions

| Placeholder | Value | Where it's used |
|-------------|-------|-----------------|
| `{{VOLTDB_VERSION}}` | `15.2.0` | `pom.xml` → `<voltdb.version>` and `<volt-procedure-api.version>` (voltdbclient + volt-procedure-api are currently released in lockstep) |
| `{{VOLTDB_IMAGE_VERSION_DEV}}` | `15.2.0_voltdb` | Developer Edition image tag (`voltactivedata/volt-developer-edition:<tag>`) — used in `test.properties` and `IntegrationTestBase.getImageVersion()` default |
| `{{VOLTDB_IMAGE_VERSION_ENT}}` | `15.2.0` | Enterprise Edition image tag (`voltdb/voltdb-enterprise:<tag>`) |
| `{{VOLT_TESTCONTAINER_VERSION}}` | `1.12.0` | `pom.xml` → `<volt-testcontainer.version>` |

## Substitution Rule (CRITICAL)

Other rule files contain literal `{{...}}` placeholders from the table above. **Before emitting any generated file** (`pom.xml`, `test.properties`, `IntegrationTestBase.java`, etc.):

1. Read this file.
2. Replace every `{{PLACEHOLDER}}` occurrence with the value from the table.
3. **Never emit a `{{...}}` placeholder into the user's project.** If a placeholder ends up in generated output, that is a bug — re-read this file and resubstitute.

The `{{...}}` form is intentionally distinct from Maven's `${...}` syntax: `${voltdb.version}` is a Maven property reference that **must** appear verbatim in `pom.xml`; `{{VOLTDB_VERSION}}` is a skill-internal placeholder that **must** be substituted before emission. The `[...]` form is also reserved (it marks user-specific values like `[AppName]`, `[PRIMARY_TABLE]`).

## Bumping versions

When VoltDB or volt-testcontainer publishes a new release:
1. Update the value column above.
2. Verify end-to-end with `mvn verify` against a scaffolded project for both Developer Edition and Enterprise.
3. No other files need editing.

## If voltdbclient and volt-procedure-api desync

They are currently aligned (both `15.2.0`), but historically they have diverged (e.g., `14.3.1` / `15.0.0`). If they desync again:
1. Add a `{{VOLT_PROCEDURE_API_VERSION}}` placeholder row above.
2. Change `rules/proj-setup.md` line for `<volt-procedure-api.version>` from `{{VOLTDB_VERSION}}` to `{{VOLT_PROCEDURE_API_VERSION}}`.
3. Restore the "Note: volt-procedure-api uses a different version from voltdbclient" comment in `proj-setup.md` near that dependency.

# Core development (build, docs, packaging)

Scope: internal (repo contributor workflow).

## Use the canonical doc first

- `README.md` is the source of truth for:
  - Build prerequisites (JDK/Maven/Docker/license)
  - Internal Maven settings (`etc/settings.internal.xml`)
  - Documentation build dependencies
  - Docker image build/push notes
  - License header checks and formatting
  - Integration test notes

## Typical workflows (commands live in `README.md`)

- Build everything: `mvn clean install`
- Skip slow/optional steps when iterating:
  - Docs: `-Pno-docs`
  - License checks: `-Pno-license`
  - Docker image build: `-Pno-docker`

## Fixes for common local build problems

- If you hit internal compiler errors during build, delete `volt-stream-plugin-infrastructure/target`.

## Hygiene rules (apply broadly)

- Ensure new files end with a newline.
- After changes, optimize imports and address IDE warnings (for example unused `throws`).

## If Maven artifacts are missing

- `README.md` documents internal-only dependencies and where they come from.

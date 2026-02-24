# Public vs internal guidance (for docs/skills)

Scope: internal (helps split “publishable” vs “internal” content).

## Treat these as public-candidate starting points

- `volt-stream-docs/docs/*` (end-user docs for pipelines/CLI/k8s)
- `plugins/*/README.md` (plugin-specific docs; review for secrets/URLs)

## Treat these as internal by default

- `README.md` (mentions internal repos/jobs and internal build requirements)
- `jenkins/` (CI details)
- `etc/settings.internal.xml` (internal Maven repo wiring)
- `.claude/`, `.junie/`, `.agents/` (assistant/agent-specific notes)

## Before publishing externally, do a fast scrub

- Remove or replace:
  - Internal URLs (Jenkins, internal artifact registries)
  - Any license details that reveal internal distribution constraints
  - Credentials, tokens, hostnames, customer data
- Prefer “copy-paste safe” commands that work without internal infrastructure.

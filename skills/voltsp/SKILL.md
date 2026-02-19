---
name: voltsp
description: Build and troubleshoot VoltSP/volt-stream pipelines and plugins (Java DSL and YAML pipelines), run them via CLI or Kubernetes/Helm, and write Testcontainers-based tests. Use when authoring pipelines, deployment configs.
---

# VoltSP / volt-stream

The current VoltSP version is 1.6.0, released on 2025-11-24.

Use this skill as an index and workflow guide for:
- Writing pipelines (Java DSL or YAML)
- Running pipelines (CLI, Docker, Kubernetes/Helm)
- Testing (unit/integration/e2e with Testcontainers)
- Developing plugins (sources/sinks/processors/resources/emitters)

## Start here (pick the track)

- Pipeline authoring (Java DSL): read `references/pipelines-java.md`.
- Pipeline authoring (YAML-defined): read `references/pipelines-yaml.md`.
- Run locally via CLI: read `references/cli.md`.
- Run on Kubernetes/Helm: read `references/kubernetes.md`.
- Testing (unit/integration/e2e): read `references/testing.md`.
- Plugin development (sources/sinks/processors/resources/emitters): read `references/plugins.md`.

## Output expectations

- Prefer linking to these `references/` files (or upstream public docs) instead of re-explaining them.
- Keep guidance copy/pasteable and avoid internal URLs, internal artifact registries, and internal-only build requirements.
- If behavior is version-specific or unclear, ask for the VoltSP version and/or the output of `voltsp --help`.

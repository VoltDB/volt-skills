---
name: voltsp-dev
description: Internal VoltSP/volt-stream contributor workflows: build and troubleshoot the repo, develop core modules, plugins, docs, charts, and test infrastructure (Java DSL, YAML pipelines, CLI, Kubernetes/Helm, Testcontainers). Use when changing this repo’s implementation or internal-facing docs/tooling.
---

# VoltSP / volt-stream (internal)

Use this skill as an index and workflow guide for:
- Writing pipelines (Java DSL or YAML)
- Developing plugins (sources/sinks/processors/resources/emitters)
- Running pipelines (CLI, Docker, Kubernetes/Helm)
- Testing (unit/integration/e2e with StreamEnvExtension + VoltSpContainer)
- Contributing to core (build, docs, module layout, internal troubleshooting)

## Start here (pick the track)

- Pipeline authoring (Java): read `references/pipelines-java.md`, then `volt-stream-docs/docs/develop.md` and `volt-stream-docs/docs/configuring-pipeline.md`.
- Pipeline authoring (YAML): read `references/pipelines-yaml.md`, then `volt-stream-docs/docs/yaml.md`.
- Operator reference (sources/sinks/processors/resources/emitters):
  - Start at `volt-stream-docs/docs/sources/index.md` (and `.../sinks/index.md`, `.../processors/index.md`, `.../resources/index.md`, `.../emitters/index.md`).
  - For generated operator pages, build docs and use `volt-stream-docs/target/{sources,sinks,processors,resources,emitters}/*.md` or `volt-stream-docs/target/website/*.html`.
- Plugin development: read `references/plugins.md`, then `references/plugins/developing_plugins_llm.md`.
- Run on Kubernetes/Helm: read `references/kubernetes.md`, then `volt-stream-docs/docs/quickstart/kubernetes.md`, `volt-stream-docs/run/kubernetes.md`, and `volt-stream-chart/README.md`.
- Run via CLI (bare metal): read `references/cli.md`, then `volt-stream-docs/docs/commandline.md`.
- Testing: read `references/testing.md`, then `volt-stream-junit-extension/README.md` and `volt-stream-docs/docs/building-testing-and-deploying.md`.
- Repo/module orientation (core dev): read `references/repo-map.md` and `references/core-dev.md`.

## Output expectations

- Prefer linking to canonical docs already in this repo instead of re-explaining them.
- When adding new guidance, put it in `references/` and keep it short, task-focused, and copy/pastable.
- If content is internal-only or environment-specific, mark it clearly in the reference file.
- If something is safe to publish externally, move it to the public skill (`voltsp-public`) and keep internal-only details here.
- When deciding what is safe to publish externally, read `references/publishing.md`.

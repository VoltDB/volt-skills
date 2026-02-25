# Kubernetes / Helm

Scope: public-candidate (deployment workflow + pointers).

## Use the canonical docs first

- Quickstart walkthrough: `volt-stream-docs/docs/quickstart/kubernetes.md`
- “Run on Kubernetes” (build/config/run): `volt-stream-docs/run/kubernetes.md`
- Helm chart details + management console: `volt-stream-chart/README.md`
- k8s troubleshooting/profiling notes: `volt-stream-docs/docs/troubleshooting.md`

## Things to clarify up front (before changing manifests)

- Where does the pipeline definition live?
  - Java pipeline class inside a pipeline JAR (`streaming.voltapps`)
  - Or YAML-defined pipeline file (run `YamlConfiguredPipeline` + set `-Dvoltsp.pipeline.definitionFile=...`)
- Which knobs are set via Helm values vs Java system properties?
  - See `volt-stream-docs/docs/confighelm.md` and `volt-stream-docs/docs/configuring-pipeline.md`.

## Operational checks

- Verify pods start: `kubectl get pods`
- Inspect logs: `kubectl logs <pod>`
- Confirm Prometheus/Loki integration if using the management console (see `volt-stream-chart/README.md`).

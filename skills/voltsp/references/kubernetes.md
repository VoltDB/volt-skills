# Kubernetes / Helm

Use this when deploying VoltSP to Kubernetes via Helm.

## Prereqs

- Kubernetes cluster + `kubectl`
- Helm
- A valid VoltSP license file
- Access to the VoltSP chart + images for your organization

## Typical workflow

1) Build your pipeline JAR:

- `mvn clean package`

2) Ensure Helm chart repos are configured (example):

```shell
helm repo add voltdb https://voltdb-kubernetes-charts.storage.googleapis.com
helm repo update
```

3) Create a `values.yaml` with resources + pipeline entry point:

```yaml
replicaCount: 1

resources:
  limits:
    cpu: 2
    memory: 2G
  requests:
    cpu: 2
    memory: 2G

streaming:
  pipeline:
    className: com.acme.MyPipeline
    configuration:
      # your app config (read via configurator.findByPath(...))
      tps: 100
```

4) Install:

```shell
export MY_VOLT_LICENSE=$HOME/licenses/volt-license.xml

helm install my-pipeline voltdb/volt-streams               \
  --set-file streaming.licenseXMLFile=${MY_VOLT_LICENSE}   \
  --set-file streaming.voltapps=target/my-pipeline.jar     \
  --values values.yaml
```

Notes:

- Chart/property names can differ by VoltSP version; confirm with your chart docs.
- You can also “auto-configure” built-in sinks/sources by putting their config under `streaming.pipeline.configuration.{source|sink|processor}.*`.

Operational checks:

- `kubectl get pods`
- `kubectl logs <pod>`

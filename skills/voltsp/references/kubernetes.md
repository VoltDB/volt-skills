# Kubernetes / Helm

Use this when deploying VoltSP to Kubernetes via Helm.

## Prerequisites

- Kubernetes cluster + `kubectl`
- Helm
- A valid VoltSP license file
- Access to the VoltSP chart and compatible images

## Typical workflow

1. Build pipeline app JAR:

- `mvn clean package`

2. Refresh chart repos:

```shell
helm repo add voltdb https://voltdb-kubernetes-charts.storage.googleapis.com
helm repo update
```

3. Define release values:

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
  longRunning: true
  pipeline:
    className: com.acme.MyPipeline
    configuration:
      generator:
        tps: 100
    configurationSecure: {}
```

4. Install:

```shell
export MY_VOLT_LICENSE=$HOME/licenses/volt-license.xml

helm install my-pipeline voltdb/volt-streams               \
  --set-file streaming.licenseXMLFile=${MY_VOLT_LICENSE}   \
  --set-file streaming.voltapps=target/my-pipeline.jar     \
  --values values.yaml
```

## Configuration behavior

- Put custom app values under `streaming.pipeline.configuration`.
- Put secrets under `streaming.pipeline.configurationSecure`.
- Auto-configure built-in operators by setting values under:
  - `streaming.pipeline.configuration.source.*`
  - `streaming.pipeline.configuration.processors.*`
  - `streaming.pipeline.configuration.sink.*`
- If both Helm configuration and Java DSL set same operator field, Java DSL value takes precedence.

## Horizontal scaling

- HPA applies only when `streaming.longRunning: true`.
- Typical settings:
  - `autoscaling.enabled`
  - `autoscaling.minReplicas`
  - `autoscaling.maxReplicas`
  - `autoscaling.targetCPUUtilizationPercentage`
  - `autoscaling.targetMemoryUtilizationPercentage`

# This section describes the Helm chart values for Volt.
The Helm charts for Volt are released into `https://voltdb-kubernetes-charts.storage.googleapis.com`.
VoltDB chart is saved under `voltdb/voltdb` and VoltSP chart is saved under `voltdb/volt-streams`.
Use `helm search repo voltdb` to find the latest version.

`voltdb` contains other charts, but this document focuses on `voltdb/voltdb` and `voltdb/volt-streams`.

## values.yaml
Helm is a source of values for values.yaml. Use `helm show values CHART` to see the latest values.
Choose `--versions=XXX` to see previous versions.

Example:
**VoltSP values.yaml**:
```yaml
global:
  voltdbVersion: "<version>"

cluster:
  clusterSpec:
    replicas: 1
    # initForce: true
    # Delete PVCs on helm upgrade, this can wipe all your data if you care
    # init will not run if you have pvc and voltdbroot is already initialized there
    # no init means the schema will not be loaded
    # deletePVC: true

    resources:
      requests:
        memory: "10Gi"
        cpu: 3
      limits:
        memory: "10Gi"
        cpu: 3

    persistentVolume:
      size: 16Gi
      storageClass: "standard-rwo"

    env:
      VOLTDB_OPTS: "-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=*:5005"

    allowRestartDuringUpdate: true

  config:
    deployment:
      cluster:
        kfactor: 0
        sitesperhost: 3

      commandlog:
        enabled: false
      snapshot:
        enabled: false
```
### VoltDb configuration highlights
#### Exporters
- Topics: For more details on topics configuration see `references/volt-helm-topics.md`

**VoltSP values.yaml**:
```yaml
replicaCount: 1
image:
  repository: voltdb/volt-streams
  tag: latest

resources:
  requests:
    memory: "5Gi"
    cpu: 3
  limits:
    memory: "5Gi"
    cpu: 3

streaming:
  pipeline:
    className: org.voltdb.stream.producer.ProducerPipeline
    configuration:
      source:
        generate:
          tps: 100
      sink:
        voltdb-procedure:
          voltClientResource:
            servers: ${ env:voltdb-master-server }
```
## Node counts
Always start from `1` node per release cluster to speed up the deployment.
Let the user decide later to increase the node count.

## Node resources
Always set same values for `resources.requests` and `resources.limits`.
For VoltDB, it is recommended to start with `cpu` number bigger or equal to `sitesperhost`. Start with 3.
For VoltDB, it is recommended to start with `memory` number to at least `10Gi`.
For VoltDB, it is recommended to start with `cpu` number bigger or equal to `parallelism`, for a start it can be set to 3.
For VoltSP, it is recommended to start with `memory` number between `2Gi` and `5Gi`.

## VoltDB Scaling Behavior Reference
1. Always Use Odd Node Counts (1, 3, 5, 7)
Prevents split-brain during network partitions:
- Even nodes (4): can split 2-2 → no majority → data corruption risk
- Odd nodes (5): can split 3-2 → group of 3 has majority → safe

2. kfactor Requirements
- For testing the deployment scribe kfactor=0 is enough.
- For production deployments consider replication kfactor=1 or higher.
- Enables data replication
- Scales 2 nodes at a time (K+1 rule): 3→5→7
- **CRITICAL**: kfactor is set at cluster creation. Must delete PVCs to change it.

| kfactor | Min Nodes | Scales By | Path | Notes                                              |
|---------|-----------|-----------|------|----------------------------------------------------|
| 0 | 1 | 1 | 1→2→3 | No replication, data loss risk, enough for testing |
| 1 | 3 | 2 | 3→5→7 | **Recommended**                                    |
| 2 | 3 | 3 | 3→6→9 | Higher redundancy                                  |

## Versions
Verify the version of `voltdb` or `volt-streams` charts with a user. Also verify the version of the images.

## Resources managed by voltdb/voltdb chart
Check with the helm chart which resources are managed by the chart. The most common resources are:
- PVCs
- Services - client, topics, vmc
- StatefulSet
- Deployment of nodes
- ConfigMap - schema config map, deployment config map
- Secret - license file
- 
## Resources managed by voltdb/volt-streams chart
Check with the helm chart which resources are managed by the chart. The most common resources are:
- PVCs
- Deployment of nodes
- ConfigMap - jar config map, configuration config map
- Secret - license file

## VoltDB lifecycle
VoltDB has multiple lifecycle stages.
- Initialization
- Start
- Rejon

Helm initializes certain resources only once, like PVCs and Secrets. 
For example, if the Pvc exists and VoltDB has already initialized `voltroot` directory, the subsequent `helm upgrade --install` will not update schema even if the file has changed.
To update those db resources, sqlcmd tool has to be called explicitly.

If `cluster.clusterSpec.forceInit` is set to `true`, the `voltroot` directory will be deleted and recreated.
If `cluster.clusterSpec.deletePVC` is set to `true`, the whole pvc will be deleted.
Those two settings can be handy for testing, but not for production.

## VoltSP lifecycle
VoltSP has only one lifecycle stage.
- Start

To apply any changes to the deployment, the pod has to be stopped and started again.
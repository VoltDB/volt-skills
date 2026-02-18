# This section describes the Helm chart values for VoltDB.
The Helm charts for Volt are releases into `https://voltdb-kubernetes-charts.storage.googleapis.com`.
VoltDB chart is saved under `voltdb/voltdb` and VoltSP chart is saved under `voltdb/volt-streams`.
Use `helm search repo voltdb` to find the latest version.

## values.yaml
Helm is a source of values for values.yaml. Use `helm show values CHART` to see the latest values.
Choose `--versions=XXX` to see previous versions.

Example:
**VoltSP values.yaml**:
```yaml
global:
  voltdbVersion: "15.1.0"

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
      VOLTDB_OPTS: "-XX:+UseTransparentHugePages"

    allowRestartDuringUpdate: true

  config:
    #schemas:
    #  products: |
    #    CREATE TABLE products
    #    EXPORT TO TOPIC cdc ON INSERT, UPDATE, DELETE
    #    WITH KEY (order_id)
    #    (
    #        order_id BIGINT NOT NULL,
    #        inserted_at TIMESTAMP NOT NULL,
    #        amount BIGINT NOT NULL
    #    );
    #
    #   PARTITION TABLE products ON COLUMN order_id;
    #
    #   CREATE PROCEDURE PRODUCTS_INSERT
    #   AS INSERT INTO PRODUCTS VALUES (?, NOW(), ?);

    deployment:
      cluster:
        kfactor: 0
        sitesperhost: 3

      # Topics configuration for CDC
      #topics:
      #  enabled: true
      #  topic:
      #    - name: cdc
      #      format: json
      #      retention: 1dy
      #      properties:
      #        "consumer.skip.internals": false

      commandlog:
        enabled: false

      snapshot:
        enabled: false

      security:
        enabled: false

      ssl:
        enabled: false

  # if topics are enabled, configure kafka erviceSpec to expose them
  #serviceSpec:
  #  type: "NodePort"
  #  kafka:
  #    type: LoadBalancer
  #    annotations:
  #      volt: "kafka"
  #    publicIPFromService: true
```

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
## Versions
Verify the version of `voltdb` or `volt-streams` charts with a user. Also verify the version of the images.

## resources managed by voltdb/voltdb chart
Check with the helm chart which resources are managed by the chart. The most common resources are:
- PVCs
- Services - client, topics, vmc
- StatefulSet
- Deployment of nodes
- ConfigMap - schema config map, deployment config map
- Secret - license file
- 
## resources managed by voltdb/volt-streams chart
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
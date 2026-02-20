# monitoring
Prometheus will scrape all pods in the cluster. By default, prometheus looks for pods under the same namespace.
This setting can be changed by setting the `monitorOwnNamespace=false` parameter.
By default, promethues scrapes pod having ServiveMonitor or PodMonitor annotations.

There are two approaches to monitoring Volt.

## Prometheus and Grafana are installed in the k8s cluster.
Before releasing Volt's pods, make sure the management-console is installed.
In this case both VoltDB and VoltSP can be monitored with the same prometheus instance.
Prometheus is configured to search for pods with ServiceMonitor annotations.
Example of VoltDB release configuration:
```yaml
cluster:
  config:
    deployment:
      metrics:
        enabled: true
```

Example of VoltSP release configuration:
```yaml
monitoring:
  prometheus:
    enabled: true

  # monitoring console can out of the box start profiler, 
  # mind that pyroscopeUrl must point to existing pyroscope service
  #profiler:
  #  enabled: true
  #  pyroscopeUrl: http://<monitoring-console-release-name>-pyroscope.<namespace>.svc.cluster.local:4040
  #  # one of ALLOC, CTIMER, WALL
  #  event: "ALLOC"
  #  extraArguments:
```

## Prometheus is not installed in the k8s cluster, and a user requires a single VoltSP release.
Enable monitoring for VoltSP release:
```yaml
management-console.enabled=true
```
In this case all VoltSP pods are going to be monitored out of the box.
The prometheus searches for pods labeled with `label: "app.kubernetes.io/name=volt-streams"`.
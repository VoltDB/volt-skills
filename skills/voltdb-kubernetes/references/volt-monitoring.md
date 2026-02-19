# monitoring
Prometheus will scrape all pods in the cluster. By default, prometheus looks for pods under the same namespace.
This setting can be changed by setting the `monitorOwnNamespace=false` parameter.
By default, promethues scrapes 

There are two approaches to monitoring. 
## Prometheus and Grafana are installed in the k8s cluster.
In this case both VoltDB and VoltSP can be monitored with the same prometheus instance.
Prometheus is configured to search for pods with ServiceMonitor annotations.
Example of VoltDB release configuration:
```yaml
metrics:
  enabled: true
```

Example of VoltSP release configuration:
```yaml
monitoring:
  prometheus:
    enabled: true

  profiler:
    enabled: true
    pyroscopeUrl: http://<monitoring-console-release-name>-pyroscope.<namespace>.svc.cluster.local:4040
    # one of ALLOC, CTIMER, WALL
    event: "ALLOC"
    extraArguments:
```

## Prometheus is not installed in the k8s cluster, and a user only wants to install VoltSP pods.
In this case all VoltSP pods are going to be monitored out of the box.
The prometheus searches for pods labeled with `label: "app.kubernetes.io/name=volt-streams"`.
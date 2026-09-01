# XDCR (Active(N)) on Kubernetes — working recipe and failure modes

Everything below was verified on VoltDB 15.3.0 / operator+chart 3.13.0 (and cross-checked
on 15.2.0 and bare Docker) during a production PoC. XDCR failures are frequently SILENT —
the cluster reports `DRROLE = XDCR / PENDING` and logs nothing — so this reference leads
with the checklist that makes it work, then the diagnosis map for when it doesn't.

## 0. Check the license FIRST

The DR producer is gated on the **`DR` feature flag** in the license. `Active(N)` alone is
NOT sufficient: with `Active(N)="true"` but no `DR="true"`, the cluster accepts
`role: xdcr`, DRROLE shows `XDCR PENDING`, and `voltadmin inspect` even derives
`XDCR="true"` — but the replication listener (port 5555) **never binds**, consumers loop
`Connection refused`, and **no error or warning is ever logged**. The only tells:

- boot log: `DR ready: false, dynamic schema: true, role state: N/A`
- `@Statistics DRROLE`: `SUPPORTED_DR_PROTOCOL = -1`
- no process listening on the replication port on any pod

Verify before anything else:
```bash
grep -E 'name="(DR|Active\(N\))"' license.xml     # need BOTH flags
```

## 1. The configuration that works (ALL required, on BOTH clusters)

```yaml
cluster:
  config:
    deployment:
      dr:
        id: 1                       # unique 0-127 per cluster
        role: xdcr
        connection:
          enabled: true             # yes, on BOTH clusters — no source-less anchor on k8s
          source: "<other-release>-voltdb-cluster-dr.<other-ns>.svc.cluster.local:5555"
    schemas:
      ddl.sql: |                    # schema WITH `DR TABLE` declarations AT CLUSTER INIT
        ...tables + DR TABLE statements...
  serviceSpec:
    dr:
      enabled: true                 # DR discovery service — REQUIRED for the listener wiring
      type: ClusterIP               # same-k8s XDCR; LoadBalancer/NodePort for cross-cluster
    perpod:
      type: ClusterIP
      dr:
        enabled: true
```

Key facts behind each line:

- **The DR network stack arms only at cluster INIT/boot.** `voltadmin set
  deployment.dr.connection.*` updates the config of a running cluster but does NOT open
  the replication port. If any of the above was missing at init, restart the cluster after
  fixing it.
- **Schema with `DR TABLE` declarations must be in the boot catalog** — deliver it via
  `cluster.config.schemas`. If the DDL contains `CREATE PROCEDURE ... FROM CLASS`,
  also deliver the classes jar at init via `cluster.config.classes` (helm
  `--set-file cluster.config.classes.db=app.jar`, or helmfile `set: {name, file:}`) so
  the full DDL compiles at init. Without the jar at init, split the DDL: tables +
  DR TABLE at init, then load classes + procedures post-start with sqlcmd.
- Symmetric sources are fine even though the peer doesn't exist yet — consumers retry DNS.
- Deployment config lands in the Secret `<release>-voltdb-cluster-init` key
  `deployment.yaml`, NOT in the VoltDBCluster CR (`spec.dr` stays `{}` even when DR is
  configured). Verify there:
  `kubectl get secret <release>-voltdb-cluster-init -o jsonpath='{.data.deployment\.yaml}' | base64 -d`

## 2. Verifying the mesh

```bash
sqlcmd --query="exec @Statistics DRROLE 0"
# healthy pre-peer: XDCR PENDING, SUPPORTED_DR_PROTOCOL >= 0 once negotiated
# healthy meshed:   XDCR ACTIVE <remote-cluster-id>
```
Raw TCP test of the listener (from any pod):
`python3 -c "import socket; socket.create_connection(('<release>-voltdb-cluster-dr.<ns>.svc.cluster.local',5555),3)"`

## 3. Replacing a failed / destroyed XDCR cluster (runbook)

Learned step by step; every step guards a real failure mode.

1. **Do not resurrect a dirty-dead cluster in place.** Recovery from the PVCs of a cluster
   that died mid-node-drain crash-looped (`UnsatisfiedLinkError: no snappyjava` during ZK
   snapshot shipping). Reinitialize instead — XDCR repopulates it (fast: a full ~14M-row
   sync completed in under 2 minutes at PoC scale).
2. **Quiesce before reinstalling**: wait for PVC deletion AND the old CR's finalizer to
   complete. A lingering finalizer deleted a freshly-installed CR minutes after
   `helm install` reported success (release "deployed", zero resources).
3. **On the survivor**: `voltadmin dr reset --cluster <deadId> --force` to forget the dead
   instance's identity (`--force` without `--cluster` when only one stale peer exists —
   the `--cluster` form errors if the id was never fully registered). Note: a command-log
   recover resurrects pre-reset DR state — reset again after any recover.
4. **If the survivor's replication port is closed, check for PAUSE first**: a paused
   cluster (including the resource monitor's RSS auto-pause) closes its DR producer port;
   `voltadmin resume` re-opens it — no restart needed. Check `CLUSTERSTATE` via
   `@SystemInformation OVERVIEW`. If the survivor is genuinely wedged, restart it:
   `voltadmin shutdown` then **delete the pods** (the operator does not restart an
   in-band shutdown by itself). A cleanly-shut-down cluster recovers its data.
5. **Leader elections are sticky**: if two clusters both self-elect
   ("This is the leader DR cluster. Waiting for other clusters to join"), their consumers
   STOP dialing and the deadlock never resolves on its own. Cycle the EMPTY cluster's pods
   while the data-holder is up, unpaused and listening — it re-runs the election, joins
   the data-holder, and syncs (full ~14M-row resync measured at ~1–2 min).

## 4. Sizing note: the survivor after a DC failover

With one DC dead and the other carrying the combined write load, the survivor's dataset
grows at the combined ingest rate. VoltDB's resource monitor (default RSS limit 80%)
pauses the database (read-only) when hit — by design, instead of OOMing. Size each DC for
the combined post-failover write growth for the intended exposure window, or cap growth
with TTL/`USING MIGRATE` lifecycle. Tune `deployment.systemsettings.resourcemonitor.memorylimit`.

## 5. Related operator/tooling gotchas

- **helm v4 breaks chart 3.13.0**: all image fields render empty
  (`spec.container.image: null`), including the chart's own uninstall hooks. Pin helm 3.x
  (brew installs helm 4 as a helmfile dependency — check `helm version` after installing
  helmfile; helmfile accepts `--helm-binary`).
- **Never delete the Volt statefulset manually**: the operator desyncs into a "No Nodes"
  reconcile loop and never issues start. Recover by restarting the operator pod; prefer a
  clean reinstall of the release.
- The operator will not roll an UNFORMED cluster's statefulset after CR resource changes —
  fix pod sizing before first formation.
- For DC-kill tests driven by node-pool resizes (GKE): don't pin the pool autoscaler
  (min=max fights manual resizes behind uncancellable reconciles), and note that pool
  operations are serialized and **silently rejected** while another op runs — always check
  the returned operation status.

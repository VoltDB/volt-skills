---
name: volt-kubernetes
description: Helps deploying VoltDB cluster on Kubernetes. Use when user wants to create scripts creating clusters on Kubernetes with Volt's releases. Use when user asks to create terraform, helmfile or helm scripts. Use when user want to create configuration as code.
---

# Helper for deploying VoltDB's cluster on Kubernetes
This skill focuses on creating cluster configuration as code using terraform, helmfile and helm.
Helm tool is used to configure kubernetes resources for a VoltDB cluster, called a release.
Helmfile tool is used to manage multiple helm releases.
Terraform tool is used to create and manage cloud resources and high-level kubernetes resources.

All those tools are using scripts, the code, that can be checked into a git repository and that can evolve in time.
After a change is approved, a specific tool should be re-run to update resources.
This skill helps to automate that process.

## Important note about resource management
Terraform can execute helm with the helm-release resource, but we have found it to be unreliable.
Both terraform and helm depend on some internal state and those two are not always compatible.
That's why I want deployment scripts to be layered. Terraform as a cloud orchestrator and helm as a kubernetes orchestrator.
Helmfile is used to manage multiple helm releases and must be run from terraform.

If some kubernetes resources are not strictly related to a cluster deployment, those can be created and managed by terraform.
For example, namespaces, config maps, pvc-s, secrets, etc.

Helm creates some kubernetes resources implicitly by setting values for the release. Those resources must be created and managed by helm.
If in doubt, always check the helm chart and clarify with a user.

## Prerequisites
Before generating deployment scripts, check that:
- **Helm v4.1.1+** is installed
- **kubectl v1.34.2+** is installed
- **Helmfile v1.2.3+** is installed
- **Terraform v1.5.7+** is installed
- **Java 17+** is installed
- **Maven 3.6+** is installed
- Valid **VoltDB Enterprise license** file is available

kubectl must be configured to connect to a cloud provider.

## Instructions
### Step 1: Understand the application details
Before any code is generated, verify with a user that there is a running integration test using testcontainers.
Such a test validates all required VoltDB components — helm values file, schema file, license, optional java code that can be packaged into a jar file.
Such a test validates all required VoltSP components — helm values file, license, optional java code that can be packaged into a jar file.
Such a test can be easily translated into a helm configuration.
If a user cannot point to such a test, please recommend creating one and quit.
**If a user selects a testcontainer test, please run it locally and verify that it passes.**

### Step 2: Script directory layout
given the application location, create a directory structure at the root of the application:
```text
k8s/
  helmfile/
    stateValues/
      base.yaml
    values/
      release-1.yaml
    helmfile.yaml.gotmpl
    .gitignore
    README.md
  terraform/
    .gitignore
    README.md
```

### Step 3: Helm values
Look at the testcontainers test and identify all Volt services that are deployed and their resources like schema, deployment file, jar files, configuration, etc.
For each identified cluster deployment, create a yaml file with the same name as the cluster.
Those yaml files must be created in root project directory under 'k8s/helmfile/values' directory.
If the directory is missing, create it.

See `references/volt-helm-release.md` for additional details.

### Step 4: Helmfile releases
Helmfile require a strict directory structure.
Looking from the `helmfile` root, it should follow this pattern:
```text
helmfile/
  stateValues/
  - base.yaml
  - env.yaml.gotmpl
  - override.yaml.local
  - override.yaml.local.template
  - .gitignore
  values/
  helmfile.yaml.gotmpl
  README.md
```
The README.md file with instructions on how to run helmfile. Helmfile can be run from terraform which should pass environment variables to helmfile. If helmfile is run from shell `terraform output name` commnad is used to get values for required environment variables.
The `helmfile.yaml.gotmpl` file contains helmfile release configuration.
The `stateValues` directory contains *.yaml or *.yaml.gotmpl files with helmfile values.
The base.yaml file contains the default values for all releases.
The env.yaml.gotmpl file contains values that are specific to the environment. Extract env value using `{{ requiredEnv "ENV_NAME" }}`. The helmfile will use keys defined in this file rather than extracting them from env.
The override.yaml.local file contains values that are specific to the local environment. This one should not be checked in as it can contain sensitive data. Make sure adding it to .gitignore.
The override.yaml.local.template file contains a template for the override.yaml.local file, with blank values.

#### Environment
The helmfile.yaml.gotmpl should configure all releases using a default environment:
```yaml
environments:
  default:
    values:
    - stateValues/base.yaml
    - stateValues/env.yaml.gotmpl
    - path: stateValues/override.yaml.local
      required: false
```
User can later add more environments, but this is a good starting point.

#### Docker Pull Secret
In order to pull images from private repositories, kubernetes requires a secret with credentials.
The helmfile could release such a secret, but it's better to create it using terraform.

#### Helm Repository
See `references/volt-helm-release.md` for information how to configure helm repository.
Verify whether additional repositories are required and include them in the helmfile.yaml.gotmpl file.
Example:
```yaml
repositories:
  - name: voltdb
    url: https://voltdb-kubernetes-charts.storage.googleapis.com
  # any other valid helm repository for kafka, prometheus, etc.
```

#### Releases
Helmfile can manage any number of releases.
Example, for the `products` application:
```yaml
releases:
  # VoltDB Products
  - name: voltdb-products
    chart: voltdb/voltdb
    version: "{{ .StateValues.voltdb.chart.version }}"
    namespace: {{ .StateValues.namespace | quote }}
    values:
      - values/voltdb-products-values.yaml
    set:
      - name: global.voltdbVersion
        value: {{ .StateValues.voltdb.version | quote }}
      - name: cluster.config.licenseXMLFile
        file: {{ .StateValues.licensePath | quote }}
      - name: cluster.config.schemas.products
        file: {{ .StateValues.voltdb.resources.products.schemaPath | quote }}
      - name: cluster.config.classes.products
        file: {{ .StateValues.voltdb.resources.products.jarPath | quote }}
      - name: cluster.clusterSpec.imagePullSecrets[0].name
        value: {{ .StateValues.docker.pullImageSecretName | quote }}

  # VoltSP Products
  - name: voltsp-products
    chart: voltdb/volt-streams
    version: "{{ .StateValues.voltsp.chart.version }}"
    namespace: {{ .StateValues.namespace | quote }}
    needs:
      - voltdb/voltdb-products
    values:
      - values/voltsp-products-values.yaml
    set:
      - name: streaming.licenseXMLFile
        file: {{ .StateValues.licensePath | quote }}
      - name: streaming.voltapps
        file: {{ .StateValues.voltsp.resources.products.jarPath | quote }}
      - name: imagePullSecrets[0].name
        value: {{ .StateValues.docker.pullImageSecretName | quote }}
      - name: podEnv.kafka-bootstrap-servers
        value: voltdb-master-cluster-0-kafka.{{ .StateValues.namespace }}.svc.cluster.local:9092
      - name: podEnv.voltdb-replica-server
        value: voltdb-replica-cluster-client.{{ .StateValues.namespace }}.svc.cluster.local:21212
```
Note that the `voltsp-products` depends on the `voltdb-products` release.
Note that the `podEnv` section contains environment variables that are used by the VoltSP configuration in helm's values.yaml file.
See `references/volt-helm-release.md` for information how to configure helm values.

#### Optional Observability release
**Propose to a user whether to include an observability release.**

As the cluster is created from scratch, the assumption is that monitoring services are not installed.
Volt uses Prometheus and Grafana for monitoring. See `references/volt-monitoring.md` for information how to enable monitoring.
Prometheus creates special kubernetes resources to correctly target and scrape metrics from pods.
By default, Prometheus is looking for pods in the same namespace.
Example of the standalone prometheus and grafana releases:
```yaml
releases:
  - name: prometheus
    chart: prometheus-community/prometheus-operator-crds
    namespace: {{ .StateValues.namespace | quote }}

  - name: monitoring
    chart: voltdb/management-console
    namespace: {{ .StateValues.namespace | quote }}
```
Mind that prometheus and grafana require additional cpu and memory resources.
Monitoring has to be released first.

### Step 5: Terraform resources
Terraform should define a frame for deployment. 

#### Questions to ask
**Ask a user the following questions:**
- which cloud provider to use
- what is the project name
- what is the project namespace
- what type of nodes the k8s will use
- whether to use a single node pool or to use multiple node pools for better transparency and isolation
- what is region and zone for deployment
- how nodes are visible to each other, should there be a specific security rules
- how nodes are accessible from the outside
- what is the name of the docker pull secret (default `dockerio-registry`) – user should provide additional email, user, password – those should be saved in terraform.tfvars file
Answer to those questions will drive values in variables.tf file.

Terraform resources are created in the root project directory under 'k8s/terraform' directory.
The terraform directory should contain the 
- .gitignore file, ignoring at least the following files:
  ```text
  terraform/*.tfvars
  terraform/.terraform
  terraform/terraform.plan
  terraform/terraform.tfstate
  terraform/terraform.tfstate.backup
  ```
- README.md file with instructions on how to run terraform
- variables.tf file
- terraform.tfvars.template file with placeholders for sensitive values that will override defaults from the variables.tf file. A user must copy this file to terraform.tfvars and fill in the values
- outputs.tf file
- provider.tf file with cloud provider configuration
- cluster.tf file with cluster configuration, pools, security rules, network rules, etc.
- namespace.tf file with namespace configuration, the global secrets, etc.
- kubectl.tf file with kubectl configuration for created project and cluster 
- release.tf file with helmfile execution, helmfile should always be executed by terraform with specific environment variables. The `helmfile apply` must be executed, and it will figure out whether the state has changed or not. This file should include any additional post-create actions once helmfile has finished.

#### Docker Pull Secret
In namespace.tf create a secret, with a default name `dockerio-registry`. Make sure variables containe placeholders for email, user and password, that can be overridden in terraform.tfvars file.
User can choose different name for the secret. The secret name should be added to a output.tf file.
The downstream helmfile config should use the same secret name.
Example:
```terraform
resource "kubernetes_secret" "dockerio_registry" {
  metadata {
    name      = "dockerio-registry"
    namespace = kubernetes_namespace.voltdb.metadata[0].name
  }

  type = "kubernetes.io/dockerconfigjson"

  data = {
    ".dockerconfigjson" = jsonencode({
      auths = {
        "https://index.docker.io/v1/" = {
          username = var.docker_username
          password = var.docker_password
          email    = var.docker_email
          auth     = base64encode("${var.docker_username}:${var.docker_password}")
        }
      }
    })
  }

  depends_on = [<other_resource_name>]
}
```

### Step 6: Verify the deployment
Run `terraform apply` command.
Verify that the deployment is working as expected.
Wait for specific pod to be ready - `kubectl wait --for=condition=ready pod -l release=<release_name> -n ${namespace} --timeout=300s;` or call `kubectl get pods -n <namespace>` and check that all pods are running without any errors. 

#### Troubleshooting
If expected pods are missing, crashing or have exited with error, check pods logs or deployment events with `kubectl describe` command.
Once event or logs are checked, propose a correction to the helmfile release configuration or to the terraform resources.
Re-run `terraform apply` command and check that all pods are running without any errors.

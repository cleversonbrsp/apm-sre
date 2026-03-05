# Lab 05 – Pipelines and Kubernetes manifests

**Objective:** Understand the **pipeline** deploy flow (build → push → download manifests → apply) and practice **reading and interpreting** a workflow and a real deployment in the K8s manifests repo.

**Note:** Repository names and paths have been generalized. Use the real names from your environment.

---

## Prerequisites

- Access to the application repository and the K8s manifests repository.
- Basic knowledge of YAML and GitHub Actions (or other CI).
- Labs 01 and 02 done.

---

## Part 1 – Deploy pipeline structure

### Step 1.1 – Choose a workflow

1. Open the **.github/workflows/** folder of the main application repository.
2. Pick a deploy workflow for one environment (e.g. pipeline for staging or prod).
3. List the main **jobs** or **steps** in order: build, test, build image, push, download manifests, apply.

### Step 1.2 – Map the steps

For the chosen workflow, fill in (or note):

| Step | What happens | Where in the workflow (step or job name) |
|------|--------------|------------------------------------------|
| 1 | Checkout code | |
| 2 | Maven build (or equivalent) | |
| 3 | Docker image build | |
| 4 | Push image to registry | |
| 5 | Download deployment.yaml from manifests repo | |
| 6 | Apply to cluster (kubectl apply) | |

**Tip:** Look for “docker build”, registry name, “curl” or API to download manifests, “kubectl apply”.

### Step 1.3 – Image and tag

- Which **registry** and **repository** are used? (e.g. `<registry>/<tenant>/<image>`.)
- Where does the image **tag** come from? (e.g. version step or `VERSION` variable.)
- Does the downloaded **deployment.yaml** reference that same image and tag? (The pipeline may replace the tag in the YAML before apply.)

**Verification:** If someone renames the deployment file in the manifests repo (e.g. from `deployment.yaml` to `deploy.yaml`), what must change in the pipeline?

---

## Part 2 – Manifests in the K8s manifests repo

### Step 2.1 – Organization by environment

1. Open the **k8s/** folder of the manifests repo and list the top-level directories (staging, prod, etc.).
2. For **staging**, go into **app-manifest/connect/** (or equivalent) and list the files (deployment, service, hpa, etc.).
3. Open the **deployment.yaml** for staging and identify:
   - Deployment **namespace**.
   - **image** (registry + name + tag).
   - **CLOUD_PROFILE** and **JVM_OPTIONS** (as in Lab 02).

### Step 2.2 – Differences between environments

Compare the **deployment.yaml** for staging with the one for prod (if it exists). Note at least two differences (e.g. replicas, resources, CLOUD_PROFILE, image tag).

**Why?** Each environment can have different resources, profiles and tags; each environment’s pipeline downloads the manifest **for that** environment.

### Step 2.3 – Cluster-manifest (SignOz, Ingress)

1. In **k8s/staging/cluster-manifest/** (or equivalent), list the folders (e.g. signoz, ingress, nginx).
2. In the SignOz folder (e.g. **cluster-manifest/signoz/k8s-infra/**), open **values.yaml** (or template) and find the **endpoint** configuration for the Otel Collector or SigNoz (e.g. `otelCollectorEndpoint`). Is that what applications use for `OTEL_EXPORTER_OTLP_ENDPOINT`? (It may be a cluster Service.)

---

## Part 3 – Simulate a safe change (dry-run)

**Objective:** Practice changing a manifest **locally** and see what would be applied **without** applying to a real cluster.

### Step 3.1 – Local copy of the deployment

1. Copy the application’s **deployment.yaml** for staging to a working directory (e.g. `lab05-workspace/deployment.yaml`).
2. Change **only** one non-critical value, for example:
   - A **label** in `metadata.labels` (e.g. add `lab: lab05`).
   - Or a **resource request** (e.g. change `memory: "6Gi"` to `memory: "4Gi"` in the copy).

### Step 3.2 – Validate and dry-run

- Validate the YAML (syntax): use an online validator or `kubectl apply -f deployment.yaml --dry-run=client -o yaml` (this does not apply to the cluster; it only validates and shows what would be applied).
- If you had access to the staging cluster, the real command would be something like: `kubectl apply -f deployment.yaml -n staging --dry-run=server` (validates on the server without applying).

**Verification:** What is the difference between `--dry-run=client` and `--dry-run=server`? (Check kubectl documentation.)

---

## Part 4 – Apply order in a full deploy

When doing a “from scratch” deploy or a new environment, in what order would you apply resources? (Use the procedure document and Lab 01.)

1. Namespace (if it does not exist).
2. Secrets (imagePullSecrets, etc.).
3. ConfigMaps (if any).
4. Deployment (then Service, HPA, Ingress per team process).

**Optional task:** In the application pipeline, is there application of **Service** and **HPA** in addition to the Deployment? If yes, in which steps and in what order?

---

## References

- [00_overview_environment](../00_overview_environment.md) – Deploy flow
- [01_stack](../01_stack.md) – Pipelines and manifests
- Deploy procedure document (workspace repository)
- .github/workflows/ of the application repository
- k8s/ of the K8s manifests repository

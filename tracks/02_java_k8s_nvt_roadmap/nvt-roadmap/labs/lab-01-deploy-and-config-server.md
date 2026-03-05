# Lab 01 – Deploy flow and Config Server

**Objective:** Understand the **deploy dependency order** and locate where each piece is configured (config-properties, Config Server, manifests, pipelines).

**Note:** Paths and repository names have been generalized. Use the real names from your environment.

---

## Prerequisites

- Access to the workspace repository (local clone).
- Read chapters [00_overview_environment](../00_overview_environment.md) and [01_stack](../01_stack.md).
- Optional: deploy procedure document at the repo root (configuration order, files per step).

---

## Part 1 – Configuration order (theory + mapping)

### Step 1.1 – List the official order

1. Open the **deploy procedure document** for your environment (at the workspace repo root or where the team indicates).
2. Find the **configuration order** section (table with 1st to 8th or equivalent).
3. Write down the order:
   - 1st: …
   - 2nd: …
   - through the last step.

**Why?** In practice, deploy failures often come from something not configured in the right order (e.g. starting the app before Config Server).

### Step 1.2 – Map real files

For each item in the table, locate **one** corresponding file or folder in the workspace repository:

| Order | What to configure   | Example path (use your repo names) |
|-------|---------------------|------------------------------------|
| 1st   | Application properties | `config-properties/` – list `*.properties` files. |
| 2nd   | Config Server       | `config-server/` – where is `application.properties` with Git URI? |
| 3rd   | Infra (cluster, registry) | (Outside repo – note “cluster, registry, compartment”). |
| 4th   | K8s manifests       | `repo-manifests-k8s/k8s/staging/app-manifest/connect/` – list files. |
| 5th   | Build artifacts      | `repo-infra/` – where is `opentelemetry-javaagent.jar`? |
| 6th   | Credentials         | (CI secrets, imagePullSecrets – note “secrets”). |
| 7th   | Cluster ready       | (Namespaces, Ingress – note “cluster-manifest”). |
| 8th   | Code and pipeline   | `app-connect/.github/workflows/` – list a deploy workflow. |

Fill in with the real paths in your environment.

**Verification:** Can you explain why Config Server should be “2nd” and the main application “8th”?

---

## Part 2 – Config Server and properties

### Step 2.1 – Config-properties repository layout

1. Go into the **config-properties** repository (real name in your environment).
2. List files that define application profiles (e.g. `connect.properties`, `connect-profile-staging.properties`).
3. Open one profile file and identify:
   - A **datasource** property (URL, user).
   - A **Config Server URL** or other service URL property (if any).

**Why?** The application does **not** embed these configs in the image; it fetches them from Config Server using the profile (`CLOUD_PROFILE`).

### Step 2.2 – How does the application know which profile to use?

1. Open the application’s **deployment.yaml** in staging (e.g. `repo-manifests-k8s/k8s/staging/app-manifest/connect/deployment.yaml`).
2. Find the **CLOUD_PROFILE** environment variable.
3. Check: the value (e.g. `profile-staging`) should appear as a suffix in a file in config-properties (e.g. `connect-profile-staging.properties`).

**Verification:** If you set `CLOUD_PROFILE` to a value that does not exist in the properties repo, what tends to happen when the pod starts?

---

## Part 3 – Deploy flow summary

Draw or write in 4 lines:

1. Where **configuration** lives (repository).
2. What **serves** that configuration at runtime (service).
3. Where the application **image** is published (registry).
4. Where the **manifests** that run the application live (repository + cluster).

**Optional task:** Open a deploy workflow (e.g. pipeline for staging) and identify in order: image build step, push to registry, deployment download, `kubectl apply`.

---

## References

- [00_overview_environment](../00_overview_environment.md)
- [01_stack](../01_stack.md)
- Deploy procedure document (workspace repository)

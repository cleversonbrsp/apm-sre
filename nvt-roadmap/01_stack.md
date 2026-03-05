# Stack – Applications, Config, Infra, and Pipelines

Details of the **stack** in the reference environment for interpreting manifests, pipelines, and troubleshooting in the labs.

**Note:** Application and repository names have been generalized to avoid exposing the company.

---

## 1. Java applications (Spring Boot)

### 1.1 Main application (Connect)

- **Structure:** monorepo with portal (main app) and modules; Maven build, multiple Dockerfiles per environment/client.
- **Runtime config:** Spring Cloud Config; profile set by `CLOUD_PROFILE` (e.g. `profile-staging`, `profile-prod-oci`). Properties come from the **config-properties** repository.
- **Typical port:** 9090 (HTTPS in container).
- **Useful endpoints:** `/portal/ping`, `/portal/health` (used in probes when enabled).
- **APM:** OpenTelemetry agent (`opentelemetry-javaagent.jar`) injected via `JVM_OPTIONS` in the Deployment; OTLP to collector/SigNoz.

### 1.2 Microservices (internal platform)

- **Services:** core, orchestrator, timefence, pubapi, config-server, among others.
- **Config:** platform config-server and microservices config-properties repository.
- **Cluster:** manifests in `repo-manifests-k8s/k8s/<cluster>/` (prod, staging, variants); Envoy, SignOz, Config Server as part of cluster-manifest.

### 1.3 Config Server

- Spring Boot application that exposes the Config Server; needs Git (config-properties) and, if encryption is used, keystore (bootstrap/application).

---

## 2. Centralized configuration (Config Server)

- **Role:** serve `application` + `profile` (e.g. `connect`, `profile-staging`) as properties/YAML.
- **Source:** Git repository (config-properties); URI and credentials in Config Server (`spring.cloud.config.server.git.uri`, etc.).
- **Client:** `spring-cloud-starter-config`; on startup, the app calls the Config Server using `CLOUD_PROFILE` and loads the properties.
- **Order:** Config Server must be up and reachable **before** starting pods that depend on it; otherwise startup fails.

---

## 3. Infrastructure (cloud, cluster, registry)

- **Cluster:** Managed Kubernetes (e.g. OKE) – clusters per environment (prod, staging, etc.).
- **Registry:** image repository (e.g. `<registry>/<tenant>/<image>:<tag>`). Pipelines push after build; Pods use `imagePullSecrets` for pull.
- **Namespaces:** per environment (e.g. `staging`, `prod`). Manifests applied with `-n <namespace>`.

---

## 4. Kubernetes manifests (repo-manifests-k8s)

- **app-manifest:** per application and environment (e.g. `k8s/staging/app-manifest/connect/deployment.yaml`, `service.yaml`, `hpa.yaml`).
- **cluster-manifest:** shared cluster resources: ingress, SignOz (k8s-infra, otel-collector, otel-agent), Envoy, configserver, nginx, etc.
- **Typical Deployment content:**
  - `env`: `CLOUD_PROFILE`, `JVM_OPTIONS` (heap, flags, `-javaagent` OpenTelemetry, OTLP endpoint).
  - `resources`: `requests`/`limits` for CPU and memory (e.g. 4 CPU, 6Gi).
  - `ports`: 9090.
  - Probes (liveness/readiness/startup) – when enabled, use `/portal/health` and `/portal/ping`.
  - `imagePullSecrets`, `nodeSelector`, `dnsConfig` as needed for the environment.

---

## 5. Pipelines (GitHub Actions)

- **General pattern:** checkout → Maven build → Docker build (with `Dockerfile.*`) → push to registry → download `deployment.yaml` (and others) from **repo-manifests-k8s** via GitHub API → replace image/tag if needed → `kubectl apply -f deployment.yaml -n <namespace>`.
- **Artifacts:** certificates and `opentelemetry-javaagent.jar` from **repo-infra** (copied in build or via secrets).
- **Variables/Secrets:** cloud provider credentials (tenancy, user, key, region), registry (username, auth token), cluster (kubeconfig or OCID), namespace, image name, etc.

---

## 6. Observability

- **OpenTelemetry Java Agent:** included in the image; configured via `JVM_OPTIONS` (`-javaagent:...`, `Dotel.exporter.otlp.endpoint`, `Dotel.resource.attributes=service.name=...`). The OTLP endpoint points to the **collector** (hostname or internal cluster IP).
- **Backend:** SigNoz (deployed via repo-manifests-k8s in cluster-manifest); OTLP collector receives traces/metrics and sends to SigNoz.
- **Day-to-day use:** traces in SigNoz for latency and errors; JVM and app metrics when exposed; logs to container stdout (and aggregated by the cluster logging stack).

---

With this stack map, you can follow the labs (deploy, Java on K8s, OTel/SigNoz, troubleshooting, pipelines and manifests) in your environment.

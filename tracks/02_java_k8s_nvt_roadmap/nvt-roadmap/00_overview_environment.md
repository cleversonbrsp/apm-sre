# Reference environment overview

This chapter describes the **reference environment** used in the labs and SRE checklist: the set of repositories and flows in your **local clone of the workspace repository**.

**Note:** Repository and component names have been generalized to avoid exposing the company. Adapt them to the real names in your environment.

---

## 1. Document purpose

- Provide a single context for all roadmap labs.
- Clarify the **dependency order** (config → infra → deploy).
- Serve as a quick reference for the role of each repository and environment.

---

## 2. Main repositories (generic names)

| Role / Repository | Summary |
|-------------------|---------|
| **app-connect** | Main application (portal + modules). Maven build, Docker image, GitHub Actions pipelines. |
| **config-server** | Spring Cloud Config Server. Serves properties from Git (config-properties repository). |
| **config-properties** | Application properties per profile (staging, prod, per-client environments). |
| **config-properties-microservices** | Microservices properties (when there is a separate suite). |
| **microservices** (orchestrator, timefence, config-server, etc.) | Internal platform services. |
| **repo-manifests-k8s** | Kubernetes manifests per cluster/environment (prod, staging, etc.), SignOz, Envoy, ingress. |
| **repo-infra** | Build artifacts: certificates (`.jks`), `opentelemetry-javaagent.jar`. |
| **other apps** | Other applications and tools in the ecosystem. |

---

## 3. Environments and clusters

- **staging** (e.g. hom) – Staging (namespace `staging` or equivalent).
- **prod** – Production.
- **client-env-a**, **client-env-b**, **demo** – Environments per client or context.
- **platform-cluster** – Microservices platform cluster (prod, staging, variants), with Envoy, SignOz, Config Server.

Manifests live under `repo-manifests-k8s/k8s/<environment>/` (e.g. `k8s/staging/app-manifest/connect/`, `k8s/<cluster>/cluster-manifest/signoz/`).

---

## 4. Deploy flow (summary)

1. **Configuration** – Properties in the config-properties repository; Config Server already deployed and healthy.
2. **Build** – Pipeline (GitHub Actions): Maven, Docker image build, push to **registry** (e.g. OCIR).
3. **Deploy** – Pipeline downloads manifests from the K8s manifests repo (e.g. `deployment.yaml`) and applies them to the cluster with `kubectl apply -n <namespace>`.
4. **Runtime** – Pod starts with `CLOUD_PROFILE` and env vars; application fetches config from Config Server on startup.

Critical order: **config (properties + Config Server) → infra (cluster, registry, secrets) → manifests → pipeline/code**.

---

## 5. Technologies in focus (for labs)

- **Applications:** Java 17+, Spring Boot, Maven; fat JAR.
- **Containers:** Docker; images in cloud registry.
- **Orchestration:** Kubernetes (e.g. OKE); Deployment, Service, HPA, Ingress.
- **Config:** Spring Cloud Config (Config Server + Git backend).
- **Observability:** OpenTelemetry (Java Agent), OTLP (HTTP/gRPC), SigNoz (cluster-manifest in manifests repo).
- **CI/CD:** GitHub Actions; build, push, download manifests, `kubectl apply`.

---

## 6. Internal documents

- **Deploy procedure:** internal document with configuration order, files per step, secrets and pipelines (check the workspace repository root).
- **Flow diagram:** reference figure for the deploy flow, if present in the repo.

Use this chapter as a starting point before each lab and when consulting the SRE checklist.

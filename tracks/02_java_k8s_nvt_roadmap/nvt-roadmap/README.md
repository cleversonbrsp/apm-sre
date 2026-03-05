# NVT Roadmap – SRE Study Material and Labs

Practical study material focused on a **reference corporate environment** (local clone of the workspace repository): Java (Spring Boot) applications on Kubernetes (OKE), Config Server, GitHub Actions pipelines, and observability with SigNoz and OpenTelemetry.

**Note:** Repository names, URLs, and environments have been generalized to avoid exposing company data. Use the material with your local clone of internal repositories.

---

## Objective

Consolidate **SRE** knowledge applied to the stack:

- **Java/Spring Boot** in containers (JVM, heap, GC, health).
- **Kubernetes (OKE)** – Deployments, resources, probes, namespaces.
- **Config Server** – Configuration order and properties per profile.
- **Pipelines** – Build, push to registry (e.g. OCIR), apply manifests (K8s manifests repository).
- **Observability** – OpenTelemetry (Java Agent), SigNoz, traces and metrics.

After completing the chapters and labs, you will be able to operate, debug, and improve deployment and observability of applications in this environment.

---

## Prerequisites

- Access to the workspace repository (local clone of internal repositories, at your path).
- Basic knowledge of: HTTP, REST, Kubernetes concepts (Pod, Deployment, Service).
- Completed (or reference) the **SRE Study Guide** chapters in `../../01_http_observability_basics/chapters/` (HTTP, Observability, APM SigNoz, SRE Best Practices).
- Local tools (for labs): Docker, `kubectl` (optional: kind/minikube), Maven 3.x, Java 17+.

---

## Material structure

```
nvt-roadmap/
├── README.md                    # This file
├── 00_overview_environment.md   # Environment overview
├── 01_stack.md                  # Stack: apps, config, infra, pipelines
├── 02_sre_checklist_java_k8s.md # SRE checklist for Java on K8s
├── labs/
│   ├── README.md                # Labs index and how to use them
│   ├── lab-01-deploy-and-config-server.md
│   ├── lab-02-java-kubernetes-resources-health.md
│   ├── lab-03-opentelemetry-signoz-java.md
│   ├── lab-04-troubleshooting-logs-dumps-metrics.md
│   └── lab-05-pipelines-and-k8s-manifests.md
└── exercises/
    └── exercises-nvt-roadmap.md # Practice exercises
```

---

## Suggested study order

1. **Reading** – `00_overview_environment.md` and `01_stack.md`.
2. **Reference** – `02_sre_checklist_java_k8s.md` (consult during incidents and deploys).
3. **Labs** – in order `lab-01` → `lab-05` (each lab consolidates one knowledge block).
4. **Practice** – `exercises/exercises-nvt-roadmap.md`.

---

## Reference environment (generic)

| Repository / Area   | Role in the roadmap |
|---------------------|----------------------|
| **app-connect** (or internal name) | Main application (portal + modules); pipelines and Dockerfile. |
| **config-server**  | Config Server; deploy order. |
| **config-properties** | Properties per profile (staging, prod, per-client environments). |
| **repo-manifests-k8s** | K8s manifests (prod, staging, etc.), SignOz, Envoy. |
| **repo-infra**     | Build artifacts: certificates, `opentelemetry-javaagent.jar`. |
| **microservices**   | Other services (orchestrator, timefence, config-server, etc.). |

Labs reference generic paths; use the real repository names in your environment.

---

## How to use the labs

- Each lab is in `labs/lab-XX-...md`.
- Follow the steps in order; where it says “workspace repository”, use your local clone of internal repositories.
- Labs that use a cluster: you can use **kind**, **minikube**, or an OKE dev/staging cluster, as indicated in each lab.

---

**Author:** Material aligned with the SRE Study Guide (apm-sre).  
**Last updated:** March 2025.

# Labs – NVT Roadmap

Hands-on labs to consolidate SRE knowledge in the reference environment (Java, Kubernetes, Config Server, OpenTelemetry, SigNoz, pipelines). Names and paths have been generalized to avoid exposing the company.

---

## Lab list

| Lab | Topic | Prerequisites |
|-----|--------|----------------|
| [Lab 01](lab-01-deploy-and-config-server.md) | Deploy flow and Config Server | Read chapters 00 and 01 of nvt-roadmap |
| [Lab 02](lab-02-java-kubernetes-resources-health.md) | Java on Kubernetes: resources, JVM and health checks | Lab 01 (recommended); Docker, kubectl |
| [Lab 03](lab-03-opentelemetry-signoz-java.md) | OpenTelemetry + SigNoz with Java application | Lab 02; Docker (and optionally K8s cluster) |
| [Lab 04](lab-04-troubleshooting-logs-dumps-metrics.md) | Troubleshooting: logs, dumps and metrics | Labs 01–03; kubectl if using real cluster |
| [Lab 05](lab-05-pipelines-and-k8s-manifests.md) | Pipelines and Kubernetes manifests | Access to app repo and K8s manifests repo |

---

## How to use

1. **Order:** do them in sequence 01 → 05 for best results.
2. **Environment:** when the lab says “workspace repository”, use your local clone of internal repositories (at your path).
3. **Cluster:** labs that use Kubernetes can be done with **kind**, **minikube**, or an OKE dev/staging cluster, as indicated in each lab.
4. **Time:** each lab may take 30 min to 1h30; allow time to read the “Why?” sections and do optional tasks.

---

## Typical lab structure

- **Objective** – What you will learn.
- **Prerequisites** – Tools and knowledge.
- **Steps** – Numbered instructions.
- **Verification** – How to confirm success.
- **Optional tasks** – Deeper practice.
- **References** – Links to chapters and internal docs.

When finished with all five labs, use the [SRE checklist](../02_sre_checklist_java_k8s.md) and [exercises](../exercises/exercises-nvt-roadmap.md) to reinforce the content.

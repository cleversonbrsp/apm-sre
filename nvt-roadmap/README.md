# NVT Roadmap – Material de Estudo e Labs SRE

Material de estudo **prático** focado em um **ambiente corporativo de referência** (clone local do repositório de trabalho): aplicações Java (Spring Boot) em Kubernetes (OKE), Config Server, pipelines GitHub Actions, observabilidade com SigNoz e OpenTelemetry.

**Nota:** Nomes de repositórios, URLs e ambientes foram generalizados para não expor dados da empresa. Use o material com seu clone local dos repositórios internos.

---

## Objetivo

Consolidar o conhecimento de **SRE** aplicado ao stack:

- **Java/Spring Boot** em containers (JVM, heap, GC, health).
- **Kubernetes (OKE)** – Deployments, recursos, probes, namespaces.
- **Config Server** – Ordem de configuração e propriedades por perfil.
- **Pipelines** – Build, push para registry (OCIR), apply de manifestos (repositório de manifestos K8s).
- **Observabilidade** – OpenTelemetry (Java Agent), SigNoz, traces e métricas.

Ao concluir os capítulos e labs, você estará apto a operar, debugar e evoluir o deploy e a observabilidade das aplicações nesse ambiente.

---

## Pré-requisitos

- Acesso ao repositório de trabalho (clone local dos repositórios internos, no caminho que você usar).
- Conhecimento básico de: HTTP, REST, conceitos de Kubernetes (Pod, Deployment, Service).
- Ter concluído (ou consultar) os capítulos do **SRE Study Guide** na pasta `../chapters/` (HTTP, Observability, APM SigNoz, SRE Best Practices).
- Ferramentas locais (para labs): Docker, `kubectl` (opcional: kind/minikube), Maven 3.x, Java 17+.

---

## Estrutura do material

```
nvt-roadmap/
├── README.md                    # Este arquivo
├── 00_visao_geral_ambiente.md   # Visão geral do ambiente
├── 01_stack_nvt.md              # Stack: aplicações, config, infra, pipelines
├── 02_sre_checklist_java_k8s.md  # Checklist SRE para Java no K8s
├── labs/
│   ├── README.md                # Índice e como usar os labs
│   ├── lab-01-deploy-e-config-server.md
│   ├── lab-02-java-kubernetes-recursos-health.md
│   ├── lab-03-opentelemetry-signoz-java.md
│   ├── lab-04-troubleshooting-logs-dumps-metricas.md
│   └── lab-05-pipelines-e-manifestos-k8s.md
└── exercicios/
    └── exercicios-nvt-roadmap.md # Exercícios de fixação
```

---

## Ordem sugerida de estudo

1. **Leitura** – `00_visao_geral_ambiente.md` e `01_stack_nvt.md`.
2. **Referência** – `02_sre_checklist_java_k8s.md` (consulta durante incidentes e deploys).
3. **Labs** – na ordem `lab-01` → `lab-05` (cada lab consolida um bloco do conhecimento).
4. **Fixação** – `exercicios/exercicios-nvt-roadmap.md`.

---

## Ambiente de referência (genérico)

| Repositório / Área        | Uso no roadmap |
|---------------------------|----------------|
| **app-connect** (ou nome interno) | Aplicação principal (portal + módulos); pipelines e Dockerfile. |
| **config-server**         | Config Server; ordem de deploy. |
| **config-properties**     | Propriedades por perfil (hom, prod, ambientes por cliente). |
| **repo-manifestos-k8s**   | Manifestos K8s (prod, hom, etc.), SignOz, Envoy. |
| **repo-infra**            | Artefatos de build: certificados, `opentelemetry-javaagent.jar`. |
| **microserviços**         | Outros serviços (orchestrator, timefence, config-server, etc.). |

Os labs referenciam caminhos genéricos; use os nomes reais dos repositórios no seu ambiente.

---

## Como usar os labs

- Cada lab está em `labs/lab-XX-...md`.
- Siga os passos na ordem; onde houver “no repositório de trabalho”, use o clone local dos repositórios internos.
- Labs que usam cluster: você pode usar **kind**, **minikube** ou um OKE de dev/homolog, conforme indicado no lab.

---

**Autor:** Material alinhado ao SRE Study Guide (apm-sre).  
**Última atualização:** Março/2025.

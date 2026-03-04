# Labs – NVT Roadmap

Laboratórios práticos para consolidar o conhecimento SRE no ambiente de referência (Java, Kubernetes, Config Server, OpenTelemetry, SigNoz, pipelines). Nomes e caminhos foram generalizados para não expor a empresa.

---

## Lista de labs

| Lab | Tema | Pré-requisitos |
|-----|------|----------------|
| [Lab 01](lab-01-deploy-e-config-server.md) | Fluxo de deploy e Config Server | Leitura dos capítulos 00 e 01 do nvt-roadmap |
| [Lab 02](lab-02-java-kubernetes-recursos-health.md) | Java no Kubernetes: recursos, JVM e health checks | Lab 01 (recomendado); Docker, kubectl |
| [Lab 03](lab-03-opentelemetry-signoz-java.md) | OpenTelemetry + SigNoz com aplicação Java | Lab 02; Docker (e opcionalmente cluster K8s) |
| [Lab 04](lab-04-troubleshooting-logs-dumps-metricas.md) | Troubleshooting: logs, dumps e métricas | Labs 01–03; kubectl se usar cluster real |
| [Lab 05](lab-05-pipelines-e-manifestos-k8s.md) | Pipelines e manifestos Kubernetes | Acesso ao repo da aplicação e ao repo de manifestos K8s |

---

## Como usar

1. **Ordem:** fazer na sequência 01 → 05 para melhor aproveitamento.
2. **Ambiente:** onde o lab pedir “no repositório de trabalho”, use o clone local dos repositórios internos (no caminho que você usar).
3. **Cluster:** labs que usam Kubernetes podem ser feitos com **kind**, **minikube** ou um OKE de dev/homolog, conforme indicado em cada lab.
4. **Tempo:** cada lab pode levar de 30 min a 1h30; reserve tempo para ler os “Por quê?” e fazer as tarefas opcionais.

---

## Estrutura típica de um lab

- **Objetivo** – O que você vai aprender.
- **Pré-requisitos** – Ferramentas e conhecimento.
- **Passos** – Instruções numeradas.
- **Verificação** – Como conferir se deu certo.
- **Tarefas opcionais** – Aprofundamento.
- **Referências** – Links para capítulos e documentos NVT.

Ao terminar os cinco labs, use o [checklist SRE](../02_sre_checklist_java_k8s.md) e os [exercícios](../exercicios/exercicios-nvt-roadmap.md) para fixar o conteúdo.

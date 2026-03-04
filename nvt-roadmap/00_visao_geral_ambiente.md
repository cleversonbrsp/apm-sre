# Visão geral do ambiente de referência

Este capítulo descreve o **ambiente de referência** usado nos labs e no checklist SRE: o conjunto de repositórios e fluxos no seu **clone local do repositório de trabalho**.

**Nota:** Nomes de repositórios e componentes foram generalizados para não expor a empresa. Adapte aos nomes reais do seu ambiente.

---

## 1. Objetivo do documento

- Dar contexto único para todos os labs do roadmap.
- Facilitar o entendimento da **ordem das dependências** (config → infra → deploy).
- Servir de referência rápida para os papéis de cada repositório e ambiente.

---

## 2. Repositórios principais (nomes genéricos)

| Papel / Repositório | Função resumida |
|---------------------|------------------|
| **app-connect** | Aplicação principal (portal + módulos). Build Maven, imagem Docker, pipelines GitHub Actions. |
| **config-server** | Spring Cloud Config Server. Serve propriedades do Git (repositório de config-properties). |
| **config-properties** | Propriedades da aplicação por perfil (hom, prod, ambientes por cliente). |
| **config-properties-microserviços** | Propriedades dos microserviços (quando houver suite separada). |
| **microserviços** (orchestrator, timefence, config-server, etc.) | Serviços da plataforma interna. |
| **repo-manifestos-k8s** | Manifestos Kubernetes por cluster/ambiente (prod, hom, etc.), SignOz, Envoy, ingress. |
| **repo-infra** | Artefatos de build: certificados (`.jks`), `opentelemetry-javaagent.jar`. |
| **outras apps** | Demais aplicações e ferramentas do ecossistema. |

---

## 3. Ambientes e clusters

- **hom** – Homologação (namespace `hom` ou equivalente).
- **prod** – Produção principal.
- **ambiente-cliente-a**, **ambiente-cliente-b**, **demo** – Ambientes específicos por cliente ou contexto.
- **cluster-plataforma** – Cluster da plataforma de microserviços (prod, hom, variantes), com Envoy, SignOz, Config Server.

Os manifestos ficam em `repo-manifestos-k8s/k8s/<ambiente>/` (ex.: `k8s/hom/app-manifest/connect/`, `k8s/<cluster>/cluster-manifest/signoz/`).

---

## 4. Fluxo de deploy (resumido)

1. **Configuração** – Propriedades no repositório de config-properties; Config Server já deployado e saudável.
2. **Build** – Pipeline (GitHub Actions): Maven, build de imagem Docker, push para o **registry** (ex.: OCIR).
3. **Deploy** – Pipeline baixa manifestos do repositório de manifestos K8s (ex.: `deployment.yaml`) e aplica no cluster com `kubectl apply -n <namespace>`.
4. **Runtime** – Pod inicia com `CLOUD_PROFILE` e variáveis de ambiente; aplicação busca config no Config Server na subida.

Ordem crítica: **config (properties + Config Server) → infra (cluster, registry, secrets) → manifestos → pipeline/código**.

---

## 5. Tecnologias em foco (para os labs)

- **Aplicações:** Java 17+, Spring Boot, Maven; fat JAR.
- **Containers:** Docker; imagens no registry da nuvem.
- **Orquestração:** Kubernetes (ex.: OKE); Deployment, Service, HPA, Ingress.
- **Config:** Spring Cloud Config (Config Server + Git backend).
- **Observabilidade:** OpenTelemetry (Java Agent), OTLP (HTTP/gRPC), SigNoz (cluster-manifest no repo de manifestos).
- **CI/CD:** GitHub Actions; build, push, download de manifestos, `kubectl apply`.

---

## 6. Documentos internos

- **Procedimento de deploy:** documento interno com a ordem de configuração, arquivos por etapa, secrets e pipelines (consulte a pasta raiz do repositório de trabalho).
- **Diagrama de fluxo:** figura de referência do fluxo de deploy, se existir no repositório.

Use este capítulo como ponto de partida antes de cada lab e ao consultar o checklist SRE.

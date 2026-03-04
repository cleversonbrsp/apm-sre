# Stack – Aplicações, Config, Infra e Pipelines

Detalhamento do **stack** do ambiente de referência para interpretar manifestos, pipelines e troubleshooting nos labs.

**Nota:** Nomes de aplicações e repositórios foram generalizados para não expor a empresa.

---

## 1. Aplicações Java (Spring Boot)

### 1.1 Aplicação principal (Connect)

- **Estrutura:** monorepo com portal (app principal) e módulos; build Maven, múltiplos Dockerfiles por ambiente/cliente.
- **Config em runtime:** Spring Cloud Config; perfil definido por `CLOUD_PROFILE` (ex.: `perfil-hom`, `perfil-prod-oci`). Propriedades vêm do repositório de **config-properties**.
- **Porta típica:** 9090 (HTTPS no container).
- **Endpoints úteis:** `/portal/ping`, `/portal/health` (usados em probes quando habilitados).
- **APM:** agente OpenTelemetry (`opentelemetry-javaagent.jar`) injetado via `JVM_OPTIONS` no Deployment; OTLP para collector/SigNoz.

### 1.2 Microserviços (plataforma interna)

- **Serviços:** core, orchestrator, timefence, pubapi, config-server, entre outros.
- **Config:** config-server da plataforma e repositório de config-properties dos microserviços.
- **Cluster:** manifestos em `repo-manifestos-k8s/k8s/<cluster>/` (prod, hom, variantes); Envoy, SignOz, Config Server como parte do cluster-manifest.

### 1.3 Config Server

- Aplicação Spring Boot que expõe o Config Server; precisa do Git (config-properties) e, se houver criptografia, do keystore (bootstrap/application).

---

## 2. Configuração centralizada (Config Server)

- **Papel:** servir `application` + `profile` (ex.: `connect`, `perfil-hom`) em formato properties/YAML.
- **Fonte:** repositório Git (config-properties); URI e credenciais no Config Server (`spring.cloud.config.server.git.uri`, etc.).
- **Cliente:** `spring-cloud-starter-config`; na subida, a app chama o Config Server usando `CLOUD_PROFILE` e carrega as properties.
- **Ordem:** Config Server deve estar no ar e acessível **antes** de subir pods que dependem dele; caso contrário, falha de startup.

---

## 3. Infraestrutura (nuvem, cluster, registry)

- **Cluster:** Kubernetes gerenciado (ex.: OKE) – clusters por ambiente (prod, hom, etc.).
- **Registry:** repositório de imagens (ex.: `<registry>/<tenant>/<imagem>:<tag>`). Pipelines fazem push após o build; Pods usam `imagePullSecrets` para pull.
- **Namespaces:** por ambiente (ex.: `hom`, `prod`). Manifestos aplicados com `-n <namespace>`.

---

## 4. Manifestos Kubernetes (repo-manifestos-k8s)

- **app-manifest:** por aplicação e ambiente (ex.: `k8s/hom/app-manifest/connect/deployment.yaml`, `service.yaml`, `hpa.yaml`).
- **cluster-manifest:** recursos compartilhados do cluster: ingress, SignOz (k8s-infra, otel-collector, otel-agent), Envoy, configserver, nginx, etc.
- **Conteúdo típico do Deployment:**
  - `env`: `CLOUD_PROFILE`, `JVM_OPTIONS` (heap, flags, `-javaagent` OpenTelemetry, endpoint OTLP).
  - `resources`: `requests`/`limits` de CPU e memória (ex.: 4 CPU, 6Gi).
  - `ports`: 9090.
  - Probes (liveness/readiness/startup) – quando ativas, usam `/portal/health` e `/portal/ping`.
  - `imagePullSecrets`, `nodeSelector`, `dnsConfig` conforme necessidade do ambiente.

---

## 5. Pipelines (GitHub Actions)

- **Padrão geral:** checkout → build Maven → build Docker (com `Dockerfile.*`) → push para registry → download do `deployment.yaml` (e outros) do **repo-manifestos-k8s** via API do GitHub → substituição de imagem/tag se necessário → `kubectl apply -f deployment.yaml -n <namespace>`.
- **Artefatos:** certificados e `opentelemetry-javaagent.jar` vêm do **repo-infra** (copiados no build ou via secrets).
- **Variáveis/Secrets:** credenciais do provedor de nuvem (tenancy, user, key, region), registry (username, auth token), cluster (kubeconfig ou OCID), namespace, nome da imagem, etc.

---

## 6. Observabilidade

- **OpenTelemetry Java Agent:** incluído na imagem; configurado via `JVM_OPTIONS` (`-javaagent:...`, `Dotel.exporter.otlp.endpoint`, `Dotel.resource.attributes=service.name=...`). O endpoint OTLP aponta para o **collector** (hostname ou IP interno do cluster).
- **Backend:** SigNoz (deploy via repo-manifestos-k8s em cluster-manifest); collector OTLP recebe traces/metrics e envia para SigNoz.
- **Uso no dia a dia:** traces no SigNoz para latência e erros; métricas JVM e de app quando expostas; logs no stdout do container (e agregados conforme stack de logging do cluster).

---

Com este mapa do stack, você consegue seguir os labs (deploy, Java no K8s, OTel/SigNoz, troubleshooting, pipelines e manifestos) no seu ambiente.

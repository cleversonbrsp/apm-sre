# Guia passo a passo: Envoy + SigNoz no cluster Kind

Este guia mostra, de forma **didática e objetiva**, como:

1. Subir o **SigNoz** em Docker no seu PC (onde o Kind também roda).
2. Fazer o **cluster Kind** (por exemplo o [kind-complete-stack](https://github.com/cleversonbrsp/kind-complete-stack)) enviar métricas do **Envoy** para o SigNoz.
3. Visualizar métricas no **dashboard Envoy** do SigNoz.

Recomendado usar o repositório **kind-complete-stack** em `/home/cleverson/Documents/crs/crs-repos/kind-complete-stack` como cluster de teste.

---

## Visão geral da arquitetura

```
┌─────────────────────────────────────────────────────────────────────────┐
│  SEU PC (host)                                                          │
│                                                                         │
│   SigNoz (Docker)          Kind cluster                                 │
│   ┌──────────────┐         ┌─────────────────────────────────────────┐  │
│   │ UI :8080     │         │  namespace: observability               │  │
│   │ OTLP :4317   │ ◄────── │ ┌─────────────┐    ┌─────────────┐      │  │
│   └──────────────┘  gRPC   │ │ OTel        │ ◄──│ Envoy       │      │  │
│        ▲                   │ │ Collector   │    │ (proxy)     │      │  │
│        │                   │ └─────────────┘    └──────┬──────┘      │  │
│        │ host.docker.      │         ▲                  │            │  │
│        │ internal:4317     │         │ métricas OTLP    │ tráfego    │  │
│        │                   │         │                  ▼            │  │
│        │                   │         │             ┌──────────┐      │  │
│        │                   │         └─────────────│ httpbin  │      │  │
│        │                   │                       └──────────┘      │  │
│        │                   └─────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

- **SigNoz (Docker):** recebe métricas na porta **4317** (OTLP gRPC) e oferece UI na **8080**.
- **OTel Collector (no Kind):** recebe métricas do Envoy e reenvia para `host.docker.internal:4317`.
- **Envoy:** faz proxy para o httpbin e envia métricas para o OTel Collector.

---

## Pré-requisitos

| Item | Verificação |
|------|-------------|
| Docker | `docker ps` funciona |
| Kind | `kind create cluster` ou cluster do **kind-complete-stack** |
| kubectl | `kubectl cluster-info` aponta para o cluster kind |
| Portas livres | 8080, 4317, 4318 (para SigNoz) |

Se usar o **kind-complete-stack**:

```bash
cd /home/cleverson/Documents/crs/crs-repos/kind-complete-stack
make rebuild
kubectl get nodes
```

---

## Parte 1 – Subir SigNoz em Docker (no host)

Objetivo: ter o SigNoz rodando no seu PC para receber métricas.

### Passo 1.1 – Clonar e subir o SigNoz

Execute **no host** (fora do cluster):

```bash
# Em um diretório de sua escolha (ex.: ~/signoz-lab)
git clone -b main https://github.com/SigNoz/signoz.git
cd signoz/deploy
```

### Passo 1.2 – Subir os containers

```bash
cd docker
docker compose up -d --remove-orphans
```

Aguarde cerca de 1–2 minutos até os containers ficarem **Up** e **healthy**.

### Passo 1.3 – Verificar

```bash
docker ps
```

Você deve ver containers como: `signoz-otel-collector`, `signoz-signoz`, `signoz-clickhouse`, etc. O collector expõe **4317** (gRPC) e **4318** (HTTP).

Acesse a UI do SigNoz:

- **URL:** [http://localhost:8080](http://localhost:8080)
- Na primeira vez, crie um usuário admin (email/senha).

Se a página abrir, a **Parte 1** está concluída.

---

## Parte 2 – Permitir que o Kind acesse o SigNoz no host

Os pods do Kind rodam *dentro* da rede do Docker. Para eles alcançarem o SigNoz no host, usamos o hostname **host.docker.internal** e garantimos que o cluster Kind o resolva.

### Passo 2.1 – Adicionar `extraHosts` no Kind

É preciso **recriar o cluster** com uma configuração que inclua `extraHosts`. Se você usa o **kind-complete-stack**, edite o arquivo `kind-cluster.yaml` e adicione em **cada nó** o bloco `extraHosts`.

**Descobrir o IP do host (para usar em `extraHosts`):**

No **Linux**, o Kind roda em containers Docker; os pods precisam do IP do host na rede Docker. Use um dos comandos abaixo e guarde o IP (ex.: `172.17.0.1`):

```bash
# Opção 1 – IP da bridge Docker
ip -4 addr show docker0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}'

# Opção 2 – Se host.docker.internal já existir (Docker Desktop ou Docker 20.10+)
docker run --rm alpine getent hosts host.docker.internal 2>/dev/null | awk '{ print $1 }'
```

No **macOS** (Docker Desktop), `host.docker.internal` já costuma funcionar; use no `extraHosts` o IP que o comando acima retornar ou, em versões recentes do Kind/Docker, `ip: host-gateway` (se suportado).

**Exemplo de `kind-cluster.yaml` (substitua `REPLACE_WITH_HOST_IP` pelo IP obtido):**

```yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: dev-cluster
nodes:
- role: control-plane
  extraHosts:
  - hostname: host.docker.internal
    ip: REPLACE_WITH_HOST_IP
  extraPortMappings:
  - containerPort: 80
    hostPort: 80
  - containerPort: 443
    hostPort: 443
- role: worker
  extraHosts:
  - hostname: host.docker.internal
    ip: REPLACE_WITH_HOST_IP
- role: worker
  extraHosts:
  - hostname: host.docker.internal
    ip: REPLACE_WITH_HOST_IP
networking:
  disableDefaultCNI: false
  apiServerAddress: "127.0.0.1"
  apiServerPort: 6443
```

### Passo 2.2 – Recriar o cluster

No **kind-complete-stack**:

```bash
make destroy
make rebuild
```

Depois:

```bash
kubectl get nodes
```

### Passo 2.3 – Testar resolução (opcional)

Crie um pod de teste e verifique se `host.docker.internal` resolve e se a porta 4317 está acessível:

```bash
kubectl run test-host --rm -it --restart=Never --image=curlimages/curl -- curl -s -o /dev/null -w "%{http_code}" http://host.docker.internal:8080/api/v1/health
```

Se retornar algo como **200** (ou o SigNoz responder), o cluster está conseguindo falar com o host. Para o collector OTLP usamos a porta **4317** (gRPC), não 8080; o importante é que o hostname resolva.

---

## Parte 3 – Deploy no Kind: OTel Collector, Envoy e httpbin

Aqui usamos os manifests do repositório **apm-sre**, na pasta da trilha 03. O Collector será configurado para enviar métricas ao SigNoz **self-hosted** no host (`host.docker.internal:4317`).

### Passo 3.1 – Criar o namespace

```bash
kubectl create namespace observability
```

### Passo 3.2 – Aplicar OTel Collector (SigNoz self-hosted)

Use o manifesto que aponta para o SigNoz em Docker no host:

```bash
# A partir da raiz do repositório apm-sre
kubectl apply -f tracks/03_envoy_signoz_metrics/signoz-envoy-proxy/k8s/otel-collector-signoz-selfhosted.yaml
```

Verifique:

```bash
kubectl get pods -n observability -l app=otel-collector
```

O pod deve estar **Running**. Se estiver CrashLoopBackOff, confira os logs:

```bash
kubectl logs -n observability -l app=otel-collector --tail=50
```

(Erros comuns: `host.docker.internal` não resolve ou porta 4317 inacessível; revise a Parte 2.)

### Passo 3.3 – Aplicar backend (httpbin) e Envoy

```bash
kubectl apply -f tracks/03_envoy_signoz_metrics/signoz-envoy-proxy/k8s/backend-httpbin.yaml
kubectl apply -f tracks/03_envoy_signoz_metrics/signoz-envoy-proxy/k8s/envoy-configmap.yaml
kubectl apply -f tracks/03_envoy_signoz_metrics/signoz-envoy-proxy/k8s/envoy-deployment.yaml
```

Verifique os pods:

```bash
kubectl get pods -n observability
```

Você deve ver algo como: `httpbin-...`, `envoy-...`, `otel-collector-...`, todos **Running**.

---

## Parte 4 – Gerar tráfego e ver métricas no SigNoz

### Passo 4.1 – Gerar tráfego através do Envoy

Em um terminal, faça port-forward do Service do Envoy:

```bash
kubectl port-forward -n observability svc/envoy 8080:8080
```

Em outro terminal, envie várias requisições para o Envoy (que repassa ao httpbin):

```bash
for i in $(seq 1 100); do curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8080/get; done
```

Mantenha o port-forward ativo; você pode repetir esse loop ou usar outras URLs (ex.: `http://localhost:8080/status/200`).

### Passo 4.2 – Ver métricas no SigNoz

1. Abra o SigNoz: [http://localhost:8080](http://localhost:8080).
2. Vá em **Dashboards** (ou **Metrics** / **Explore**).
3. Importe o dashboard Envoy do SigNoz:
   - Arquivo: [envoy-otlp-v1.json](https://github.com/SigNoz/dashboards/blob/main/envoy/envoy-otlp-v1.json)
   - No SigNoz: **Dashboards** → **Import** → faça upload do JSON.
4. As variáveis do dashboard (ex.: `service.name`, `namespace`) devem bater com o que está no Envoy (`stats_tags`): por exemplo `envoy-proxy-k8s`, `observability`, `lab`, `demo-cluster`. Selecione os valores corretos no topo do dashboard.

Você deve passar a ver métricas de tráfego, latência (P50/P95/P99) e erros relacionadas ao Envoy.

---

## Parte 5 (opcional) – SigNoz dentro do cluster Kind via Helm

Se quiser **tudo** dentro do Kind (SigNoz + Envoy + Collector), em vez de SigNoz em Docker no host:

### Passo 5.1 – Adicionar o repositório Helm

```bash
helm repo add signoz https://charts.signoz.io
helm repo update
```

### Passo 5.2 – StorageClass e values

Verifique a storage class disponível:

```bash
kubectl get storageclass
```

Crie um `values.yaml` (ex.: em `signoz-envoy-proxy/signoz-helm-values.yaml`):

```yaml
global:
  storageClass: standard   # use o nome retornado por get storageclass

clickhouse:
  installCustomStorageClass: true
```

### Passo 5.3 – Instalar SigNoz no cluster

```bash
kubectl create namespace signoz
helm install signoz signoz/signoz -n signoz --create-namespace -f values.yaml --wait --timeout 10m
```

### Passo 5.4 – Coletor apontando para o SigNoz no cluster

Nesse cenário, o OTel Collector no namespace `observability` deve enviar para o **service do SigNoz** no cluster, por exemplo:

- Endpoint: `signoz-signoz-otel-collector.signoz.svc.cluster.local:4317`

Você pode editar o ConfigMap do collector (ou usar um manifesto alternativo) e trocar o exporter para:

```yaml
exporters:
  otlp:
    endpoint: "signoz-signoz-otel-collector.signoz.svc.cluster.local:4317"
    tls:
      insecure: true
```

Depois, acesse a UI do SigNoz via port-forward:

```bash
kubectl port-forward -n signoz svc/signoz-frontend 8080:8080
```

E use [http://localhost:8080](http://localhost:8080). O restante do fluxo (Envoy → Collector → SigNoz) permanece o mesmo; apenas o destino do collector muda.

---

## Resumo dos comandos (fluxo principal)

| Ordem | Onde | Comando / Ação |
|-------|------|-----------------|
| 1 | Host | `cd signoz/deploy/docker && docker compose up -d --remove-orphans` |
| 2 | Host | Editar `kind-cluster.yaml` (extraHosts) e `make rebuild` no kind-complete-stack |
| 3 | Host | `kubectl create ns observability` |
| 4 | Host | `kubectl apply -f .../otel-collector-signoz-selfhosted.yaml` |
| 5 | Host | `kubectl apply -f .../backend-httpbin.yaml` + envoy-configmap + envoy-deployment |
| 6 | Host | `kubectl port-forward -n observability svc/envoy 8080:8080` |
| 7 | Host | `curl` em loop para `http://localhost:8080/get` |
| 8 | Browser | Abrir SigNoz em http://localhost:8080 e importar dashboard Envoy |

---

## Troubleshooting

| Problema | O que verificar |
|----------|------------------|
| Collector em CrashLoopBackOff | Logs: `kubectl logs -n observability -l app=otel-collector`. Confirme que `host.docker.internal` resolve e que a porta 4317 do host está acessível. |
| Nenhuma métrica no SigNoz | SigNoz está em 8080? OTLP na 4317? Gerou tráfego no Envoy? Variáveis do dashboard batem com as `stats_tags` do Envoy? |
| Envoy não sobe | `kubectl logs -n observability -l app=envoy`. Confirme que o ConfigMap `envoy-config` existe e que o cluster `opentelemetry_collector` aponta para `otel-collector.observability.svc.cluster.local:4317`. |
| host.docker.internal não resolve no Kind | Revisar `extraHosts` no `kind-cluster.yaml` e recriar o cluster. Em Linux, testar com o IP da bridge Docker em vez de `0.0.0.0`. |

---

## Referências

- [SigNoz – Docker Standalone](https://signoz.io/docs/install/docker)
- [SigNoz – Envoy Dashboard](https://github.com/SigNoz/dashboards/tree/main/envoy)
- Lab completo (Cloud e self-hosted): [signoz-envoy-proxy/README.md](signoz-envoy-proxy/README.md)

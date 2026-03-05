# Guia passo a passo: Envoy + SigNoz no cluster Kind

Este guia mostra, de forma **didática e objetiva**, como:

1. Subir o **SigNoz** em Docker no seu PC (onde o Kind também roda).
2. Fazer o **cluster Kind** (por exemplo o [kind-complete-stack](https://github.com/cleversonbrsp/kind-complete-stack)) enviar métricas do **Envoy** para o SigNoz.
3. Visualizar métricas no **dashboard Envoy** do SigNoz.

Recomendado usar o repositório **kind-complete-stack** em `/home/cleverson/Documents/crs/crs-repos/kind-complete-stack` como cluster de teste.

---

## Por que essa arquitetura?

- **Envoy** gera métricas (requisições, latência, erros) e as envia no formato **OTLP** (padrão OpenTelemetry). Sozinho, ele não grava em banco nem mostra gráficos — só exporta.
- O **OpenTelemetry Collector** no cluster recebe essas métricas e as **reenvia** para o SigNoz. Ele existe porque: (1) o Envoy fala OTLP gRPC; (2) o SigNoz também aceita OTLP; (3) o Collector pode fazer batching e, no nosso caso, **sair do cluster** e falar com um serviço no host (SigNoz em Docker).
- O **SigNoz** armazena as métricas (ClickHouse), permite consultas e oferece **dashboards** prontos (como o de Envoy). Rodando no host em Docker, você não precisa instalar nada pesado dentro do Kind.
- O **httpbin** é só um backend de teste: o Envoy faz proxy para ele para que haja tráfego real e, assim, métricas para visualizar.

Resumindo: **Envoy (métricas) → OTel Collector (ponte) → SigNoz (armazenamento e UI)**. Cada peça tem um papel claro.

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
│        │ 172.17.0.1:4317   │         │ métricas OTLP   │ tráfego     │  │
│        │                   │         │                 ▼             │  │
│        │                   │         │             ┌──────────┐      │  │
│        │                   │         └─────────────│ httpbin  │      │  │
│        │                   │                       └──────────┘      │  │
│        │                   └─────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

- **SigNoz (Docker):** recebe métricas na porta **4317** (OTLP gRPC) e oferece UI na **8080**. A porta 4317 é o padrão OTLP gRPC; a 8080 é a interface web.
- **OTel Collector (no Kind):** recebe métricas do Envoy e reenvia para o IP do host na rede Docker (ex.: `172.17.0.1:4317`). Ele “traduz” apenas o destino: de dentro do cluster para o host.
- **Envoy:** faz proxy para o httpbin e envia métricas para o OTel Collector. O tráfego HTTP gera as métricas; o sink OTLP envia essas métricas para o Collector.

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

**Objetivo:** ter o SigNoz rodando no seu PC para receber métricas.

**Por que no host?** Rodar o SigNoz em Docker no host (e não dentro do Kind) reduz o uso de recursos do cluster e deixa a UI sempre acessível em `localhost:8080`. O cluster Kind fica focado em Envoy, Collector e aplicações; o “cérebro” da observabilidade fica fora. Em produção você pode ter SigNoz em outro servidor ou na nuvem; o fluxo (Collector envia OTLP) é o mesmo.

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

**Por que vários containers?** O SigNoz usa ClickHouse (armazenamento), Zookeeper (coordenação) e o próprio signoz (API + UI). O **signoz-otel-collector** é o que escuta na 4317 e grava no ClickHouse. Tudo sobe junto para simular uma instalação mínima funcional.

Aguarde cerca de 1–2 minutos até os containers ficarem **Up** e **healthy**.

### Passo 1.3 – Verificar

```bash
docker ps
```

Você deve ver containers como: `signoz-otel-collector`, `signoz-signoz`, `signoz-clickhouse`, etc. O collector expõe **4317** (gRPC) e **4318** (HTTP).

Acesse a UI do SigNoz:

- **URL:** [http://localhost:8080](http://localhost:8080)

### Passo 1.4 – Primeiro acesso: criar usuário admin

Na **primeira vez** que você acessa o SigNoz self-hosted, é preciso **criar a primeira conta** (que vira admin). A tela pode mostrar só "Sign in" (e-mail + Next), **sem** link visível de "Sign up" ou "Create account".

- Acesse **http://localhost:8080** (sem `/login`). Em algumas versões, o fluxo de criação de conta aparece ao abrir a raiz.
- Use uma **janela anônima** (incognito) para evitar cookies de um acesso anterior.
- Crie a conta com um e-mail (ex.: `admin@localhost.com`) e defina uma senha. Esse usuário será o admin do workspace.
- Depois use esse mesmo e-mail e senha para **Sign in** sempre que acessar.

**Se aparecer erro `user_not_found` ("user with email ... in org ... not found"):**  
Significa que já existe um workspace (org) no banco, mas nenhum usuário foi criado nele — por exemplo, se você tentou logar antes de concluir o cadastro ou se a instalação ficou em estado inconsistente.

**Solução:** zerar os dados e subir o SigNoz de novo, para forçar o fluxo de primeiro usuário:

```bash
cd signoz/deploy/docker   # ou o caminho onde está o docker-compose do SigNoz
docker compose down -v
docker compose up -d --remove-orphans
```

Aguarde 1–2 minutos. Abra **http://localhost:8080** em janela anônima e conclua o cadastro (e-mail + senha). A partir daí use esse usuário para logar.

Se a UI abrir e você conseguir entrar com seu usuário, a **Parte 1** está concluída.

**Próximo passo:** [Parte 2](#parte-2--ip-do-host-para-o-kind) — confirmar o IP do host; em seguida [Parte 3](#parte-3--deploy-no-kind-otel-collector-envoy-e-httpbin) para fazer o deploy do Envoy no cluster.

---

## Parte 2 – IP do host para o Kind

**Por que falar do IP aqui?** Os pods do Kind rodam *dentro* de containers Docker. Para eles alcançarem um serviço que está no **host** (o SigNoz em Docker), precisam de um endereço que aponte para a máquina host. No Linux, a interface **docker0** (bridge padrão) tem um IP — em geral `172.17.0.1` — que é o “gateway” dos containers em direção ao host. Por isso o Collector envia métricas para `172.17.0.1:4317`: é o endereço do host visto de dentro da rede Docker.

**Por que não usar `extraHosts` no Kind?** Em versões atuais do Kind (API v1alpha4), o campo `extraHosts` não existe nos nós. Tentar usá-lo gera erro ao criar o cluster. A solução mais simples é usar o IP da bridge diretamente no manifesto do Collector, sem alterar o `kind-cluster.yaml`. O manifesto `otel-collector-signoz-selfhosted.yaml` já está configurado para `172.17.0.1:4317`.

### Passo 2.1 – Confirmar o IP do host (opcional)

Se o seu IP da bridge for diferente (ex.: outra rede Docker), descubra e ajuste o endpoint no Collector:

```bash
# Linux – IP da bridge docker0
ip -4 addr show docker0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}'
```

Se retornar algo diferente de `172.17.0.1`, edite o arquivo `signoz-envoy-proxy/k8s/otel-collector-signoz-selfhosted.yaml` e troque o valor em `exporters.otlp.endpoint` para `SEU_IP:4317`.

### Passo 2.2 – Cluster Kind pronto

Certifique-se de que o cluster está no ar (sem precisar de `extraHosts`):

```bash
kubectl get nodes
```

Se os nós estiverem **Ready**, siga para a Parte 3.

---

## Parte 3 – Deploy no Kind: OTel Collector, Envoy e httpbin

Aqui usamos os manifests do repositório **apm-sre**, na pasta da trilha 03. O Collector envia métricas ao SigNoz no host no endereço **172.17.0.1:4317** (ou o IP que você configurou).

**Por que namespace `observability`?** Agrupar Collector, Envoy e httpbin no mesmo namespace facilita a organização e os nomes de serviços (por exemplo `otel-collector.observability.svc.cluster.local`). Em um ambiente real você pode ter um namespace só para observabilidade e outros para aplicações.

### Passo 3.1 – Criar o namespace

```bash
kubectl create namespace observability
```

### Passo 3.2 – Aplicar OTel Collector (SigNoz self-hosted)

**Por que um Collector separado?** O Envoy envia métricas em OTLP gRPC para um endpoint que você configura. Em vez de apontar o Envoy direto para o SigNoz (que exigiria que o SigNoz estivesse acessível pelo nome de um Service no cluster), usamos um Collector *dentro* do cluster: o Envoy fala com ele (Service `otel-collector.observability`), e o Collector reenvia para o IP do host. Assim o Envoy não precisa “saber” onde está o SigNoz; só precisa conhecer o Collector.

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

(Erros comuns: porta 4317 inacessível do cluster para o host, ou IP incorreto; confira se o SigNoz está em execução e se o IP em `otel-collector-signoz-selfhosted.yaml` é o da bridge Docker.)

### Passo 3.3 – Aplicar backend (httpbin) e Envoy

**Por que httpbin?** É um serviço HTTP de teste que responde a vários paths (`/get`, `/status/200`, etc.). O Envoy atua como proxy para ele: o tráfego que passa pelo Envoy gera métricas (requisições, códigos HTTP, latência). Sem tráfego, o Envoy não teria o que exportar; o httpbin existe só para gerar esse tráfego de forma simples e reproduzível.

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

**Por que gerar tráfego?** O Envoy só exporta métricas quando há requisições passando por ele. Sem tráfego, os dashboards ficam vazios. O port-forward expõe o Service do Envoy na sua máquina (porta 8080) para que você possa enviar `curl` e simular usuários.

### Passo 4.1 – Gerar tráfego através do Envoy

Em um terminal, faça port-forward do Service do Envoy (para acessar o Envoy como se estivesse em `localhost:8080`):

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
4. **Por que as variáveis do dashboard importam?** O dashboard Envoy do SigNoz filtra métricas por atributos como `service.name`, `namespace`, `cluster`. Esses valores vêm das **stats_tags** que configuramos no Envoy (no ConfigMap). Se os valores no topo do dashboard não coincidirem (ex.: você deixou `envoy-proxy-k8s` e `observability`), os gráficos podem ficar vazios. Selecione exatamente o que está no Envoy: `envoy-proxy-k8s`, `observability`, `lab`, `demo-cluster`.

Você deve passar a ver métricas de tráfego, latência (P50/P95/P99) e erros relacionadas ao Envoy.

---

## Parte 5 (opcional) – SigNoz dentro do cluster Kind via Helm

**Por que colocar o SigNoz no cluster?** No guia principal, o SigNoz fica em Docker no host para simplificar (uma instalação só, acessível em localhost). Se você quiser um ambiente “tudo no Kind” — por exemplo para testar em um único cluster ou para espelhar um cenário em que o SigNoz roda em Kubernetes — pode instalar o SigNoz via Helm no próprio cluster. O Collector então envia para o Service do SigNoz (DNS interno) em vez do IP do host. O fluxo Envoy → Collector → SigNoz continua o mesmo; só muda o destino do exporter.

Se quiser **tudo** dentro do Kind (SigNoz + Envoy + Collector):

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
| 2 | Host | (Opcional) Confirmar IP do host com `ip -4 addr show docker0 ...`; cluster Kind já no ar |
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
| Collector em CrashLoopBackOff | Logs: `kubectl logs -n observability -l app=otel-collector`. Confirme que o SigNoz está rodando no host e que o endpoint no Collector é o IP correto da bridge Docker (ex.: `172.17.0.1:4317`). |
| Nenhuma métrica no SigNoz | SigNoz está em 8080? OTLP na 4317? Gerou tráfego no Envoy? Variáveis do dashboard batem com as `stats_tags` do Envoy? |
| Envoy não sobe | `kubectl logs -n observability -l app=envoy`. Confirme que o ConfigMap `envoy-config` existe e que o cluster `opentelemetry_collector` aponta para `otel-collector.observability.svc.cluster.local:4317`. |
| Collector não alcança o SigNoz | O Kind não usa `extraHosts`; o Collector aponta para o IP do host (ex.: `172.17.0.1:4317`). Se o IP da bridge for outro, edite `otel-collector-signoz-selfhosted.yaml` e reaplique. |

---

## Referências

- [SigNoz – Docker Standalone](https://signoz.io/docs/install/docker)
- [SigNoz – Envoy Dashboard](https://github.com/SigNoz/dashboards/tree/main/envoy)
- Lab completo (Cloud e self-hosted): [signoz-envoy-proxy/README.md](signoz-envoy-proxy/README.md)

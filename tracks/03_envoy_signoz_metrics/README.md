# Track 3 – Envoy + SigNoz Metrics

Conteúdo para aprender a **coletar métricas do Envoy Proxy** e visualizá-las no **SigNoz** usando OpenTelemetry. O foco é didático: cada passo explica o **porquê**, não só o “como”.

---

## Por que Envoy + SigNoz?

O **Envoy** é um proxy que gera muitas métricas úteis (requisições, latência, erros por upstream). Sozinho, ele só as exporta em OTLP; não armazena nem mostra gráficos. O **SigNoz** é uma plataforma de observabilidade que aceita OTLP, armazena em ClickHouse e oferece dashboards prontos (incluindo um para Envoy). Conectar os dois permite ver o comportamento do proxy em tempo quase real sem escrever queries do zero. O **OpenTelemetry Collector** no meio recebe as métricas do Envoy e as envia ao SigNoz — ele é a “ponte” que permite colocar o SigNoz fora do cluster (ex.: Docker no host) enquanto o Envoy roda dentro.

---

## Objetivo

- Entender o fluxo: **Envoy** → métricas OTLP → **OpenTelemetry Collector** → **SigNoz**.
- Subir o **SigNoz** (Docker no host ou Helm no cluster).
- Fazer o **cluster Kind** (por exemplo o [kind-complete-stack](https://github.com/cleversonbrsp/kind-complete-stack)) enviar métricas do Envoy para o SigNoz.
- Visualizar métricas no **dashboard Envoy** do SigNoz.

---

## Para quem é

SREs e engenheiros de plataforma que querem monitorar Envoy (ou proxies similares) com SigNoz, em ambiente local (Kind) ou referência para produção.

---

## Ordem sugerida

1. **Guia passo a passo (Kind + SigNoz em Docker)**  
   Siga o [GUIA-ENVOY-SIGNOZ-KIND.md](GUIA-ENVOY-SIGNOZ-KIND.md). Ele cobre:
   - Subir SigNoz em Docker no host.
   - Confirmar o IP do host para o Collector (ex.: 172.17.0.1; não é necessário alterar o kind-cluster.yaml).
   - Deploy no Kind: OTel Collector, Envoy, httpbin.
   - Gerar tráfego e ver métricas no SigNoz.
   - (Opcional) SigNoz no próprio Kind via Helm.

2. **Lab completo (Cloud ou self-hosted)**  
   Use o [signoz-envoy-proxy/README.md](signoz-envoy-proxy/README.md) para detalhes do Collector (Cloud vs self-hosted), configuração do Envoy e importação do dashboard.

---

## Conteúdo da pasta

| Item | Descrição |
|------|-----------|
| [GUIA-ENVOY-SIGNOZ-KIND.md](GUIA-ENVOY-SIGNOZ-KIND.md) | **Guia principal:** passo a passo com Kind e SigNoz em Docker no host; uso opcional do kind-complete-stack. |
| [signoz-envoy-proxy/](signoz-envoy-proxy/) | Lab completo: manifests K8s (Collector, Envoy, httpbin), README com Cloud/self-hosted e troubleshooting. |
| [signoz-envoy-proxy/k8s/](signoz-envoy-proxy/k8s/) | `otel-collector.yaml` (SigNoz Cloud), `otel-collector-signoz-selfhosted.yaml` (SigNoz Docker no host), Envoy, httpbin. |

---

## Cluster Kind de teste

Se você usa o repositório **kind-complete-stack** em:

`/home/cleverson/Documents/crs/crs-repos/kind-complete-stack`

o guia [GUIA-ENVOY-SIGNOZ-KIND.md](GUIA-ENVOY-SIGNOZ-KIND.md) mostra como usar o Collector configurado para o IP do host (ex.: 172.17.0.1:4317), sem precisar alterar o kind-cluster.yaml.

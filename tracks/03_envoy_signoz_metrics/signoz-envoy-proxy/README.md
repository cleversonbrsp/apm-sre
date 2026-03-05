## Laboratório: Coleta de métricas do Envoy com SigNoz

Este laboratório guia você a configurar a coleta de **métricas do Envoy Proxy** usando **OpenTelemetry** e **SigNoz**, seguindo a documentação oficial do dashboard Envoy do SigNoz (`envoy-otlp-v1.json`) descrita em [`SigNoz/dashboards/envoy`](https://github.com/SigNoz/dashboards/tree/main/envoy).

**Se você usa cluster Kind e quer SigNoz em Docker no host (passo a passo didático):** use o [GUIA-ENVOY-SIGNOZ-KIND.md](../GUIA-ENVOY-SIGNOZ-KIND.md) nesta trilha. Ele cobre SigNoz em Docker, `extraHosts` no Kind e o uso do arquivo `k8s/otel-collector-signoz-selfhosted.yaml`.

O foco deste README é:

- **Configurar um OpenTelemetry Collector** recebendo métricas OTLP do Envoy.
- **Configurar o Envoy** para enviar métricas via `envoy.stat_sinks.open_telemetry`.
- **Encaminhar as métricas para o SigNoz** (Cloud ou self-hosted).
- **Importar o dashboard Envoy** no SigNoz e validar as métricas.

---

## 1. Pré-requisitos

- **Cluster Kubernetes** funcional (kind, k3d, minikube, AKS, EKS, GKE, etc.).
- **kubectl** apontando para o cluster.
- Conta **SigNoz Cloud** ou instância **SigNoz self-hosted** acessível.
- **Chave de ingestão** do SigNoz (para SigNoz Cloud) ou endpoint OTLP do SigNoz self-hosted.
- Docker/OCI runtime funcional para imagens (`envoyproxy/envoy`, `otel/opentelemetry-collector-contrib`).

Assuma neste laboratório:

- Namespace de trabalho: `observability`.
- SigNoz Cloud, com:
  - `<region>` = região do SigNoz (ex.: `us`, `eu`).
  - `<your-ingestion-key>` = sua chave de ingestão.

Se você estiver usando SigNoz self-hosted, haverá anotações específicas na etapa do Collector.

---

## 2. Estrutura de arquivos deste laboratório

Todos os arquivos ficam em `tracks/03_envoy_signoz_metrics/signoz-envoy-proxy/` neste repositório:

- `README.md` (este arquivo): roteiro completo do laboratório.
- `k8s/otel-collector.yaml`: Collector para **SigNoz Cloud** (endpoint + ingestion key).
- `k8s/otel-collector-signoz-selfhosted.yaml`: Collector para **SigNoz self-hosted** (ex.: Docker no host; envia para `host.docker.internal:4317`).
- `k8s/envoy-configmap.yaml`: configuração do Envoy com stats sink OpenTelemetry.
- `k8s/envoy-deployment.yaml`: deployment + service de um Envoy frontando um backend simples.

> Obs.: os manifests são exemplos de referência para ambiente de laboratório. Adapte nomes, labels e endereços conforme sua realidade.

---

## 3. Passo 1 – Criar namespace e aplicar base

1. Crie o namespace de observabilidade:

   ```bash
   kubectl create namespace observability
   ```

2. Confirme que o namespace foi criado:

   ```bash
   kubectl get ns observability
   ```

---

## 4. Passo 2 – Configurar o OpenTelemetry Collector

Aqui vamos aplicar um Collector que:

- **Recebe métricas OTLP gRPC** na porta `4317`.
- **Encaminha para o SigNoz** usando o exporter OTLP, conforme sugerido na doc oficial do Envoy dashboard do SigNoz.

### 4.1. Manifesto do Collector

Crie o arquivo `k8s/otel-collector.yaml` com o conteúdo abaixo (ajuste `<region>` e `<your-ingestion-key>`):

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: otel-collector-config
  namespace: observability
data:
  config.yaml: |
    receivers:
      otlp:
        protocols:
          grpc:
            endpoint: 0.0.0.0:4317

    processors:
      batch:
        timeout: 10s
        send_batch_size: 1024

    exporters:
      otlp:
        # SigNoz Cloud
        endpoint: "ingest.<region>.signoz.cloud:443"
        tls:
          insecure: false
        headers:
          signoz-ingestion-key: "<your-ingestion-key>"

    service:
      pipelines:
        metrics:
          receivers: [otlp]
          processors: [batch]
          exporters: [otlp]
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: otel-collector
  namespace: observability
spec:
  replicas: 1
  selector:
    matchLabels:
      app: otel-collector
  template:
    metadata:
      labels:
        app: otel-collector
    spec:
      containers:
      - name: otel-collector
        image: otel/opentelemetry-collector-contrib:0.144.0
        args:
          - "--config=/conf/config.yaml"
        volumeMounts:
        - name: config
          mountPath: /conf
        ports:
        - containerPort: 4317  # OTLP gRPC
          name: otlp-grpc
      volumes:
      - name: config
        configMap:
          name: otel-collector-config
---
apiVersion: v1
kind: Service
metadata:
  name: otel-collector
  namespace: observability
spec:
  selector:
    app: otel-collector
  ports:
  - name: otlp-grpc
    port: 4317
    targetPort: 4317
```

> **Self-hosted SigNoz**: troque o bloco `exporters.otlp.endpoint` para o endereço do seu Otel Collector do SigNoz (por exemplo, `signoz-otel-collector.observability:4317`) e remova o cabeçalho `signoz-ingestion-key`.

### 4.2. Aplicar o Collector

```bash
kubectl apply -f tracks/03_envoy_signoz_metrics/signoz-envoy-proxy/k8s/otel-collector.yaml
kubectl get pods -n observability -l app=otel-collector
```

Certifique-se de que o pod `otel-collector` esteja em estado `Running`.

---

## 5. Passo 3 – Configurar Envoy com stats sink OpenTelemetry

Agora vamos configurar o Envoy para:

- Exportar métricas para o Collector via `envoy.stat_sinks.open_telemetry`.
- Adicionar **tags** (`stats_tags`) que serão usadas como **variáveis de dashboard** no SigNoz, conforme a doc do dashboard Envoy.

### 5.1. ConfigMap com configuração do Envoy

Crie `k8s/envoy-configmap.yaml` com o conteúdo abaixo. Os pontos-chave vêm da doc oficial:

- `emit_tags_as_attributes: true`
- `report_histograms_as_deltas: true`
- `stats_tags` para `service.name`, `namespace`, `deployment_environment`, `cluster`

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: envoy-config
  namespace: observability
data:
  envoy.yaml: |
    static_resources:
      clusters:
        - name: backend_service
          type: STRICT_DNS
          lb_policy: ROUND_ROBIN
          load_assignment:
            cluster_name: backend_service
            endpoints:
              - lb_endpoints:
                  - endpoint:
                      address:
                        socket_address:
                          address: httpbin
                          port_value: 80

        - name: opentelemetry_collector
          type: STRICT_DNS
          lb_policy: ROUND_ROBIN
          typed_extension_protocol_options:
            envoy.extensions.upstreams.http.v3.HttpProtocolOptions:
              "@type": type.googleapis.com/envoy.extensions.upstreams.http.v3.HttpProtocolOptions
              explicit_http_config:
                http2_protocol_options: {}
          load_assignment:
            cluster_name: opentelemetry_collector
            endpoints:
              - lb_endpoints:
                  - endpoint:
                      address:
                        socket_address:
                          # Nome do service do Collector no cluster
                          address: otel-collector.observability.svc.cluster.local
                          port_value: 4317

      listeners:
        - name: listener_http
          address:
            socket_address:
              address: 0.0.0.0
              port_value: 8080
          filter_chains:
            - filters:
                - name: envoy.filters.network.http_connection_manager
                  typed_config:
                    "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
                    stat_prefix: ingress_http
                    route_config:
                      name: local_route
                      virtual_hosts:
                        - name: backend
                          domains: ["*"]
                          routes:
                            - match:
                                prefix: "/"
                              route:
                                cluster: backend_service
                    http_filters:
                      - name: envoy.filters.http.router

    stats_sinks:
      - name: envoy.stat_sinks.open_telemetry
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.stat_sinks.open_telemetry.v3.SinkConfig
          grpc_service:
            envoy_grpc:
              cluster_name: opentelemetry_collector
          emit_tags_as_attributes: true
          report_histograms_as_deltas: true

    stats_config:
      stats_tags:
        - tag_name: service.name
          fixed_value: envoy-proxy-k8s
        - tag_name: namespace
          fixed_value: observability
        - tag_name: deployment_environment
          fixed_value: lab
        - tag_name: cluster
          fixed_value: demo-cluster

    admin:
      access_log_path: /dev/null
      address:
        socket_address:
          address: 0.0.0.0
          port_value: 9901
```

> Dica: ajuste os valores de `fixed_value` em `stats_tags` para refletirem seu ambiente real (ex.: `service.name: envoy-gateway-prod`, `deployment_environment: staging` etc.).

---

## 6. Passo 4 – Deploy do backend de teste e do Envoy

Vamos subir um backend simples (`httpbin`) e o Envoy como proxy frontend.

### 6.1. Backend httpbin

Crie um arquivo `k8s/backend-httpbin.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: httpbin
  namespace: observability
spec:
  replicas: 1
  selector:
    matchLabels:
      app: httpbin
  template:
    metadata:
      labels:
        app: httpbin
    spec:
      containers:
        - name: httpbin
          image: kennethreitz/httpbin
          ports:
            - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: httpbin
  namespace: observability
spec:
  selector:
    app: httpbin
  ports:
    - port: 80
      targetPort: 80
      protocol: TCP
```

### 6.2. Deployment do Envoy

Crie o arquivo `k8s/envoy-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: envoy
  namespace: observability
spec:
  replicas: 1
  selector:
    matchLabels:
      app: envoy
  template:
    metadata:
      labels:
        app: envoy
    spec:
      containers:
        - name: envoy
          image: envoyproxy/envoy:v1.31-latest
          args:
            - "-c"
            - "/etc/envoy/envoy.yaml"
          ports:
            - containerPort: 8080
              name: http
            - containerPort: 9901
              name: admin
          volumeMounts:
            - name: envoy-config
              mountPath: /etc/envoy
      volumes:
        - name: envoy-config
          configMap:
            name: envoy-config
---
apiVersion: v1
kind: Service
metadata:
  name: envoy
  namespace: observability
spec:
  selector:
    app: envoy
  ports:
    - name: http
      port: 8080
      targetPort: 8080
```

### 6.3. Aplicar backend e Envoy

```bash
kubectl apply -f tracks/03_envoy_signoz_metrics/signoz-envoy-proxy/k8s/backend-httpbin.yaml
kubectl apply -f tracks/03_envoy_signoz_metrics/signoz-envoy-proxy/k8s/envoy-configmap.yaml
kubectl apply -f tracks/03_envoy_signoz_metrics/signoz-envoy-proxy/k8s/envoy-deployment.yaml

kubectl get pods -n observability -l app=httpbin
kubectl get pods -n observability -l app=envoy
```

Garanta que os pods estejam `Running`.

---

## 7. Passo 5 – Gerar tráfego através do Envoy

Para que o SigNoz mostre métricas úteis, gere tráfego passando pelo Envoy.

1. Faça port-forward do Envoy localmente:

   ```bash
   kubectl port-forward -n observability svc/envoy 8080:8080
   ```

2. Em outro terminal, envie requisições para o Envoy (que roteia para o httpbin):

   ```bash
   for i in {1..100}; do curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8080/get; done
   ```

3. Isso deve gerar:
   - **Métricas de tráfego** (RQ total, RQ por código HTTP, etc.).
   - **Métricas de latência** (histogramas P50/P95/P99, graças a `report_histograms_as_deltas: true`).

---

## 8. Passo 6 – Importar e explorar o dashboard Envoy no SigNoz

1. Baixe o arquivo de dashboard Envoy oficial do repositório:
   - Arquivo: `envoy-otlp-v1.json`
   - Local: diretório `envoy` em [`SigNoz/dashboards/envoy`](https://github.com/SigNoz/dashboards/tree/main/envoy)

2. No SigNoz:
   - Vá em **Dashboards** → **Import**.
   - Faça upload de `envoy-otlp-v1.json`.

3. O dashboard expõe variáveis como:
   - `$service.name` (mapeado para a tag `service.name` que definimos como `envoy-proxy-k8s`).
   - `$namespace` (tag `namespace`, valor `observability`).
   - `$cluster` (tag `cluster`, valor `demo-cluster`).
   - `$deployment_environment` (tag `deployment_environment`, valor `lab`).

4. Selecione os valores corretos no topo do dashboard (de acordo com o que você configurou em `stats_tags`).

Você deve ver:

- Tráfego por código HTTP, por cluster/backend.
- Latência P50/P95/P99.
- Erros, timeouts, retried requests, etc.

---

## 9. Passo 7 – Validação e troubleshooting

Se as métricas não aparecerem:

- **Collector**:
  - Verifique logs do pod:
    ```bash
    kubectl logs -n observability deploy/otel-collector
    ```
  - Confirme se está ouvindo em `0.0.0.0:4317` e se não há erros de conexão com o SigNoz.

- **Envoy**:
  - Verifique se o cluster `opentelemetry_collector` está `healthy` via admin API:
    ```bash
    kubectl port-forward -n observability svc/envoy 9901:9901
    curl http://localhost:9901/clusters
    ```
  - Confirme se o endereço `otel-collector.observability.svc.cluster.local:4317` resolve no cluster.
  - Garanta que o tráfego está passando pelo Envoy (use `/stats` na admin API para ver counters).

- **Tags / variáveis de dashboard**:
  - Confira se as tags em `stats_config.stats_tags` batem com as variáveis esperadas pelo dashboard (`service.name`, `namespace`, `cluster`, `deployment_environment`).

---

## 10. Extensões do laboratório

Sugestões para aprofundar:

- Adicionar múltiplos Envoys (por exemplo, gateway e sidecars) com `service.name` diferentes e comparar métricas.
- Introduzir falhas no backend (`httpbin` retornando 500/503) para observar impacto em métricas de erro.
- Integrar **logs** e **traces** no SigNoz além de métricas, para visão 3 pilares.
- Usar variáveis de ambiente/Secrets para gerir `signoz-ingestion-key` em vez de colocá-la em texto plano no ConfigMap.

Com isso, você tem um laboratório completo e reproduzível para entender como o Envoy exporta métricas via OpenTelemetry e como o SigNoz consome e visualiza essas métricas usando o dashboard oficial.


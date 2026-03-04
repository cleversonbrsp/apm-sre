# Lab 03 – OpenTelemetry + SigNoz com aplicação Java

**Objetivo:** Instrumentar uma aplicação **Java** com o **OpenTelemetry Java Agent**, enviar **traces** (e opcionalmente métricas) para um **collector OTLP** e visualizar no **SigNoz**, reproduzindo o padrão usado no ambiente de referência.

---

## Pré-requisitos

- Docker e Docker Compose.
- Java 17+ e Maven (se for buildar um JAR local).
- Ter feito o [Lab 02](lab-02-java-kubernetes-recursos-health.md) (recomendado).
- Opcional: cluster Kubernetes (kind/minikube) para simular deploy com agente.

---

## Parte 1 – Entender a configuração no ambiente

### Passo 1.1 – JVM_OPTIONS no deployment

1. Abra o **deployment.yaml** da aplicação em hom (no repositório de manifestos K8s).
2. Localize a variável **JVM_OPTIONS** e copie o valor (uma linha longa).
3. Identifique:
   - `-javaagent:<caminho>/opentelemetry-javaagent.jar`
   - `-Dotel.exporter.otlp.protocol=http/protobuf`
   - `-Dotel.exporter.otlp.endpoint=http://<endpoint-coletor>:4318`
   - `-Dotel.resource.attributes=service.name=<nome-do-serviço>`

**Por quê?** O agente é carregado na JVM sem alterar código; o endpoint é o OTLP (collector) que encaminha para o SigNoz. O endpoint é o hostname ou IP do collector no cluster.

### Passo 1.2 – Onde está o agente e o collector?

- **Agente:** vem da imagem da aplicação; no build, o Dockerfile copia `opentelemetry-javaagent.jar` (ex.: do **repo-infra**) para dentro da imagem.
- **Collector/SigNoz:** no repositório de manifestos K8s, na pasta do cluster-manifest (ex.: `signoz/k8s-infra/`) há values e templates do Otel Collector e do SigNoz. O endpoint que os Pods usam é o Service do collector (hostname + porta 4317/4318).

---

## Parte 2 – Lab local: Java + OTLP + SigNoz com Docker Compose

### Passo 2.1 – Estrutura do lab

Crie um diretório para o lab (ex.: `nvt-roadmap-labs/lab03-otel-java`) com:

- Um **Dockerfile** para uma aplicação Java (Spring Boot) com o agente.
- Um **docker-compose.yml** com: app Java, Otel Collector (recebe OTLP), SigNoz (UI + backend).

Você pode reutilizar o **java-msc** do crs-repos ou qualquer Spring Boot que exponha um endpoint HTTP.

### Passo 2.2 – Baixar o OpenTelemetry Java Agent

```bash
mkdir -p lab03-otel-java/agent
cd lab03-otel-java/agent
curl -L -o opentelemetry-javaagent.jar \
  https://github.com/open-telemetry/opentelemetry-java-instrumentation/releases/latest/download/opentelemetry-javaagent.jar
cd ..
```

(Ou use o JAR do **repo-infra** do seu ambiente, se tiver acesso.)

### Passo 2.3 – Dockerfile da aplicação Java

Exemplo usando uma image base com Java e o JAR da aplicação + agente:

```dockerfile
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app

# Copiar agente OTel
COPY agent/opentelemetry-javaagent.jar /app/opentelemetry-javaagent.jar

# Copiar JAR da aplicação (ajuste o nome conforme seu build)
COPY app.jar /app/app.jar

ENV JAVA_OPTS="-Xmx256m -javaagent:/app/opentelemetry-javaagent.jar"
ENV OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
ENV OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318
ENV OTEL_RESOURCE_ATTRIBUTES=service.name=lab03-java-app

EXPOSE 8080
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -Dotel.exporter.otlp.protocol=$OTEL_EXPORTER_OTLP_PROTOCOL -Dotel.exporter.otlp.endpoint=$OTEL_EXPORTER_OTLP_ENDPOINT -Dotel.resource.attributes=$OTEL_RESOURCE_ATTRIBUTES -jar /app/app.jar"]
```

Se usar **Spring Boot** com actuator, a instrumentação automática já gera spans para HTTP. Ajuste `app.jar` para o path do seu JAR (ex.: `target/myapp-0.0.1-SNAPSHOT.jar`).

### Passo 2.4 – docker-compose.yml

Exemplo mínimo (ajuste nomes e ports conforme sua necessidade):

```yaml
services:
  app:
    build: .
    ports:
      - "8080:8080"
    environment:
      - OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318
      - OTEL_SERVICE_NAME=lab03-java-app
    depends_on:
      - otel-collector

  otel-collector:
    image: otel/opentelemetry-collector-contrib:latest
    command: ["--config=/etc/otel-config.yaml"]
    volumes:
      - ./otel-config.yaml:/etc/otel-config.yaml
    ports:
      - "4317:4317"
      - "4318:4318"

  signoz:
    image: signoz/signoz:latest
    ports:
      - "3301:3301"
    environment:
      - OTEL_COLLECTOR_SVC=otel-collector:4317
```

Crie **otel-config.yaml** para o collector receber OTLP e exportar para SigNoz (ou para o endpoint que o container SigNoz espera – consulte a doc do SigNoz para o schema exato). Exemplo simplificado:

```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

exporters:
  otlp:
    endpoint: signoz:4317
    tls:
      insecure: true

service:
  pipelines:
    traces:
      receivers: [otlp]
      exporters: [otlp]
```

### Passo 2.5 – Subir e gerar tráfego

```bash
docker-compose up --build -d
# Gerar requisições para a app (ajuste a URL se necessário)
curl http://localhost:8080/actuator/health
# Ou outros endpoints da sua app
```

Abra o SigNoz em **http://localhost:3301** e verifique a lista de **serviços** e **traces**. Você deve ver `lab03-java-app` (ou o nome definido em `OTEL_RESOURCE_ATTRIBUTES`).

**Verificação:** Um trace de uma requisição HTTP deve aparecer no SigNoz com spans gerados pelo agente (ex.: span de controller/servlet).

---

## Parte 3 – Comparar com o ambiente real

1. No cluster, o endpoint OTLP é um **hostname ou IP do Service** do collector (ex.: `http://<coletor-otel>.namespace.svc:4318`).
2. O **service.name** identifica a aplicação nos traces (ex.: nome do deployment ou do serviço).
3. No seu lab local, o collector está na mesma rede Docker que a app; no K8s, a rede do cluster permite que Pods resolvam o Service do collector.

**Tarefa opcional:** No repositório de manifestos K8s, abra o `values.yaml` (ou equivalente) da stack SignOz e localize a configuração do endpoint do collector/backend.

---

## Referências

- [01_stack_nvt](../01_stack_nvt.md) – Observabilidade
- [02_sre_checklist_java_k8s](../02_sre_checklist_java_k8s.md) – OpenTelemetry
- deployment.yaml da aplicação (JVM_OPTIONS)
- cluster-manifest SignOz no repositório de manifestos K8s

# Lab 02 – Java no Kubernetes: recursos, JVM e health checks

**Objetivo:** Configurar **recursos** (CPU/memória), **opções da JVM** e **probes** (liveness/readiness) em um Deployment de aplicação Java, alinhado ao padrão do ambiente de referência.

---

## Pré-requisitos

- Docker instalado.
- `kubectl` configurado (kind, minikube ou cluster OKE de dev/hom).
- Ter feito o [Lab 01](lab-01-deploy-e-config-server.md) (recomendado).
- Leitura do [02_sre_checklist_java_k8s](../02_sre_checklist_java_k8s.md) (seção Recursos e Probes).

---

## Parte 1 – Analisar um Deployment real

### Passo 1.1 – Recursos e JVM no deployment da aplicação

1. Abra o **deployment.yaml** da aplicação principal em hom (ex.: `repo-manifestos-k8s/k8s/hom/app-manifest/connect/deployment.yaml` no seu repositório de trabalho).
2. Localize:
   - **resources** (requests/limits de CPU e memory).
   - **env** com **JVM_OPTIONS** (incluindo `-Xmx`, `-javaagent`, `Dotel.*`).
3. Responda:
   - Qual o limit de memória? O valor em `-Xmx` é menor que esse limit? (Deve ser; a JVM usa mais que só heap.)
   - As probes (liveness/readiness) estão habilitadas ou comentadas? Se habilitadas, qual path e porta?

**Por quê?** Em muitos ambientes o padrão é limit alto (ex.: 6Gi) e heap fixo (ex.: 2g); o restante é para metaspace, threads e nativo. Probes comentadas significam que o time desativou temporariamente; em produção idealmente se usa health/ping.

### Passo 1.2 – Relação heap vs memory limit

- Memory limit do container: **6Gi** (exemplo do hom).
- `-Xmx2048m` = 2Gi de heap.
- Regra prática: heap ≈ 70–80% do limit em app Java “normal”; o resto é metaspace + threads + código nativo.
- Se o limit fosse 2Gi e o heap 2Gi, o pod poderia ser **OOMKilled**. Por quê? (Pesquise “OOMKilled Java container” se precisar.)

---

## Parte 2 – Prática: Deployment mínimo com Java (Spring Boot)

Use uma imagem pública de exemplo (Spring Boot) ou um JAR que você já tenha. O foco aqui é **recursos + JVM + probes**, não o código.

### Passo 2.1 – Criar um Deployment de teste

Crie o arquivo `lab02-deployment.yaml` (pode ser em um diretório de trabalho qualquer):

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: java-app-lab02
  namespace: default
spec:
  replicas: 1
  selector:
    matchLabels:
      app: java-app-lab02
  template:
    metadata:
      labels:
        app: java-app-lab02
    spec:
      containers:
      - name: java-app
        image: eclipse-temurin:17-jre-alpine
        command: ["/bin/sh", "-c"]
        args:
          - |
            apk add --no-cache curl
            java -Xmx256m -XX:+UseContainerSupport -XX:MaxRAMPercentage=75.0 -jar /app/app.jar || true
        env:
        - name: JAVA_OPTS
          value: "-Xmx256m -XX:+UseContainerSupport -XX:MaxRAMPercentage=75.0"
        resources:
          requests:
            memory: "384Mi"
            cpu: "200m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        # Descomente e ajuste se sua imagem expuser health:
        # livenessProbe:
        #   httpGet:
        #     path: /actuator/health
        #     port: 8080
        #   initialDelaySeconds: 60
        #   periodSeconds: 10
        # readinessProbe:
        #   httpGet:
        #     path: /actuator/health
        #     port: 8080
        #   initialDelaySeconds: 30
        #   periodSeconds: 5
```

**Nota:** A imagem acima não tem JAR; é só para ver a estrutura. Para um teste real, use uma imagem que já tenha um Spring Boot (ex.: uma image do seu java-msc ou uma image pública como `springio/gs-spring-boot-docker`).

**Versão simplificada (só para ver pod com recursos):** use uma image que rode algo indefinidamente, por exemplo:

```yaml
# Alternativa: container que só “dorme” para testar recursos
args: ["sleep", "3600"]
# e remova o bloco command/args do java.
```

Substitua o `image` por uma image Spring Boot real se tiver; caso contrário, use algo como:

```yaml
image: eclipse-temurin:17-jre-alpine
args: ["sleep", "3600"]
```

e aplique:

```bash
kubectl apply -f lab02-deployment.yaml
kubectl get pods -w
```

### Passo 2.2 – Ajustar recursos e observar

1. Reduza o **memory limit** para um valor baixo (ex.: 128Mi) e mantenha um heap alto (ex.: `-Xmx256m`). Aplique e observe o pod (deve ficar OOMKilled).
2. Restaure um limit maior que o heap (ex.: 512Mi limit, 256m heap) e confira que o pod fica Running.

**Verificação:** Você consegue explicar por que 128Mi de limit com 256m de heap leva a OOMKilled?

---

## Parte 3 – Probes no deployment

1. Volte ao **deployment.yaml** da aplicação em hom.
2. Descomente mentalmente (ou em uma cópia local) as seções **startupProbe**, **livenessProbe** e **readinessProbe**.
3. Anote:
   - Path de liveness e de readiness (health vs ping).
   - Por que usar **HTTPS** e porta **9090** (é a porta da aplicação Connect).
   - O que acontece se `initialDelaySeconds` for pequeno demais para uma JVM + Spring Boot pesada.

**Tarefa opcional:** Em um cluster de teste, crie um Deployment com uma app Java que exponha `/actuator/health` e configure liveness e readiness; force uma falha (ex.: derrube o DB) e observe o comportamento do readiness vs liveness.

---

## Referências

- [02_sre_checklist_java_k8s](../02_sre_checklist_java_k8s.md) – Recursos e Probes
- [01_stack_nvt](../01_stack_nvt.md) – Stack e manifestos
- deployment.yaml da aplicação em hom (repositório de manifestos K8s)

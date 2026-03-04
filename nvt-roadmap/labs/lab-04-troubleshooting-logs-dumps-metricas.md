# Lab 04 – Troubleshooting: logs, dumps e métricas

**Objetivo:** Praticar **investigação de problemas** em aplicação Java no Kubernetes: **logs**, **thread dump**, **heap dump** e **métricas** (JVM/GC), alinhado a cenários comuns no ambiente de referência.

---

## Pré-requisitos

- `kubectl` configurado para um cluster (kind, minikube ou OKE).
- Ter feito os [Labs 01](lab-01-deploy-e-config-server.md) e [02](lab-02-java-kubernetes-recursos-health.md).
- Leitura da seção “Troubleshooting rápido” do [02_sre_checklist_java_k8s](../02_sre_checklist_java_k8s.md).

---

## Parte 1 – Logs do Pod

### Passo 1.1 – Onde estão os logs no K8s?

- Logs de aplicação Java costumam ir para **stdout/stderr** do container (Spring Boot default).
- Comando básico: `kubectl logs <pod> -n <namespace>`.
- Para seguir em tempo real: `kubectl logs -f <pod> -n <namespace>`.
- Se o pod reiniciou: `kubectl logs <pod> -n <namespace> --previous` (mostra o último container que morreu).

### Passo 1.2 – Exercício (leitura)

1. No **deployment** da aplicação (hom), o container usa qual **nome**? (campo `name` do container.)
2. Se você tivesse um pod `<deployment-name>-xxxxx-yyyyy` no namespace `hom`, qual comando usaria para ver os logs?
3. O que procurar em um log de **startup** quando a aplicação não sobe: erro de conexão com Config Server? Com banco? Stack trace de exceção?

**Exemplo de comando:**  
`kubectl logs <pod-name> -n hom` ou `kubectl logs -l app=<label-da-app> -n hom --tail=100`.

### Passo 1.3 – Prática (se tiver cluster com app Java)

1. Liste os pods do namespace onde roda uma app Java: `kubectl get pods -n <namespace>`.
2. Escolha um pod e execute: `kubectl logs <pod> -n <namespace> --tail=50`.
3. Identifique no log: nível (INFO, ERROR), stack trace (se houver), mensagem de conexão ao Config Server ou ao DB.

---

## Parte 2 – Thread dump

### Passo 2.1 – Para que serve?

- **Thread dump** mostra o estado de todas as threads da JVM (onde estão “travadas” ou em que método estão).
- Útil para: **deadlock**, threads bloqueadas em I/O ou em locks, alta CPU em uma thread específica.

### Passo 2.2 – Como obter no Kubernetes

- **Opção 1:** `kubectl exec <pod> -n <namespace> -- jstack 1` (1 = PID do processo Java dentro do container; em muitos casos é o único processo).
- **Opção 2:** se o container não tiver `jstack`, copiar o JAR da app e usar uma image que tenha JDK: `kubectl exec ... -- sh -c 'jstack 1 > /tmp/jstack.txt'` e depois `kubectl cp` (ou redirecionar para stdout e salvar localmente).

Em produção os containers podem ter apenas JRE; nesse caso, é comum ter um **sidecar** ou **job** com ferramentas de diagnóstico, ou usar um **ephemeral debug container** (K8s 1.23+) com JDK para executar `jstack` no processo do container principal.

### Passo 2.3 – Exercício (análise)

1. Pesquise na web: “how to analyze jstack output deadlock”.
2. Abra um exemplo de thread dump (pode ser um arquivo de exemplo na web) e localize a seção **“Found one Java-level deadlock”** (se houver). Quais threads estão envolvidas?

**Verificação:** Você sabe explicar em uma frase por que thread dump ajuda em “a aplicação não responde”?

---

## Parte 3 – Heap dump e OOMKilled

### Passo 3.1 – Quando usar

- **OOMKilled:** o container foi morto pelo Kubelet por ultrapassar o memory limit. Causa comum em Java: heap + metaspace + nativo > limit.
- **Heap dump** é um snapshot da memória heap; serve para analisar **memory leak** (quais objetos estão retendo memória).

### Passo 3.2 – Como obter heap dump no K8s

- **Em vida:** `kubectl exec <pod> -n <namespace> -- jmap -dump:live,format=b,file=/tmp/heap.hprof 1` (requer JDK no container; o arquivo fica dentro do pod).
- **Em OOM:** algumas JVMs podem gerar heap dump automático com `-XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/tmp`. O arquivo fica no filesystem do container; se o pod reiniciar, você perde. Por isso, em produção às vezes se usa volume ou sidecar que copia o dump para um storage.

No seu ambiente, verifique se há **JVM_OPTIONS** com `HeapDumpOnOutOfMemoryError` em algum deployment; se não houver, é um ponto de melhoria para incidentes de OOM.

### Passo 3.3 – Checklist rápido para OOMKilled

- [ ] Conferir `kubectl describe pod` – motivo do exit: OOMKilled?
- [ ] Comparar **memory limit** do container com **-Xmx** (e outras áreas de memória JVM).
- [ ] Se possível, coletar heap dump antes do próximo restart (ou habilitar HeapDumpOnOutOfMemoryError para o próximo evento).
- [ ] Ajustar heap (reduzir) ou aumentar memory limit (com cuidado para não esgotar o nó).

---

## Parte 4 – Métricas JVM e GC

### Passo 4.1 – Onde as métricas aparecem no NVT?

- **Spring Boot Actuator** pode expor métricas em `/actuator/prometheus` (formato Prometheus).
- **OpenTelemetry** (Java Agent) pode exportar métricas JVM (heap, GC, threads) para o mesmo backend de traces (SigNoz/collector).
- No **SigNoz**, dashboards ou métricas podem mostrar uso de heap, tempo de GC, etc., se o collector estiver configurado para receber métricas OTLP.

### Passo 4.2 – O que observar em um incidente de “lentidão”

- **GC:** pausas longas (stop-the-world) aumentam latência; métricas como “GC time” ou “pause time”.
- **Heap:** uso próximo do máximo pode indicar que a JVM está fazendo GC com muita frequência.
- **Threads:** muitas threads em estado BLOCKED ou RUNNABLE em código que segura locks pode indicar contenção.

**Tarefa:** Liste três métricas JVM que você olharia primeiro ao investigar “aplicação lenta”.

**Exemplo de resposta:** (1) Heap used vs max, (2) GC pause time (ou frequency), (3) Thread count ou thread states.

---

## Parte 5 – Cenário simulado (resumo)

Imagine: um pod da aplicação em hom está em **CrashLoopBackOff**.

1. Qual comando você usaria para ver o motivo do crash?
2. Quais três causas mais comuns você checaria (config, Config Server, DB, recursos, JVM)?
3. Onde você procuraria o endpoint do Config Server (variável de ambiente, properties no config-properties)?

Responda em texto curto; use o checklist [02_sre_checklist_java_k8s](../02_sre_checklist_java_k8s.md) como apoio.

---

## Referências

- [02_sre_checklist_java_k8s](../02_sre_checklist_java_k8s.md) – Troubleshooting rápido
- [01_stack_nvt](../01_stack_nvt.md) – Observabilidade
- Kubernetes: `kubectl logs`, `kubectl exec`, `kubectl describe pod`

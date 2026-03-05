# Lab 04 – Troubleshooting: logs, dumps and metrics

**Objective:** Practice **problem investigation** for a Java application on Kubernetes: **logs**, **thread dump**, **heap dump** and **metrics** (JVM/GC), aligned with common scenarios in the reference environment.

---

## Prerequisites

- `kubectl` configured for a cluster (kind, minikube or OKE).
- Labs 01 and 02 done.
- Read the “Quick troubleshooting” section of [02_sre_checklist_java_k8s](../02_sre_checklist_java_k8s.md).

---

## Part 1 – Pod logs

### Step 1.1 – Where are logs in K8s?

- Java application logs usually go to container **stdout/stderr** (Spring Boot default).
- Basic command: `kubectl logs <pod> -n <namespace>`.
- Follow in real time: `kubectl logs -f <pod> -n <namespace>`.
- If the pod restarted: `kubectl logs <pod> -n <namespace> --previous` (shows the last container that died).

### Step 1.2 – Exercise (reading)

1. In the application **deployment** (staging), what **name** does the container use? (container `name` field.)
2. If you had a pod `<deployment-name>-xxxxx-yyyyy` in namespace `staging`, what command would you use to see logs?
3. What to look for in **startup** logs when the app does not come up: Config Server connection error? DB? Exception stack trace?

**Example command:**  
`kubectl logs <pod-name> -n staging` or `kubectl logs -l app=<app-label> -n staging --tail=100`.

### Step 1.3 – Practice (if you have a cluster with a Java app)

1. List pods in the namespace where a Java app runs: `kubectl get pods -n <namespace>`.
2. Pick a pod and run: `kubectl logs <pod> -n <namespace> --tail=50`.
3. In the log, identify: level (INFO, ERROR), stack trace (if any), Config Server or DB connection message.

---

## Part 2 – Thread dump

### Step 2.1 – What is it for?

- A **thread dump** shows the state of all JVM threads (where they are “stuck” or which method they are in).
- Useful for: **deadlock**, threads blocked on I/O or locks, high CPU on one thread.

### Step 2.2 – How to get it in Kubernetes

- **Option 1:** `kubectl exec <pod> -n <namespace> -- jstack 1` (1 = PID of the Java process in the container; often the only process).
- **Option 2:** if the container has no `jstack`, use an image with JDK or an **ephemeral debug container** (K8s 1.23+) with JDK to run `jstack` against the main container’s process.

In production, containers may have only a JRE; then a **sidecar** or **job** with diagnostic tools, or an ephemeral debug container, is common.

### Step 2.3 – Exercise (analysis)

1. Search the web: “how to analyze jstack output deadlock”.
2. Open a sample thread dump and find the **“Found one Java-level deadlock”** section (if any). Which threads are involved?

**Verification:** Can you explain in one sentence why a thread dump helps when “the application is not responding”?

---

## Part 3 – Heap dump and OOMKilled

### Step 3.1 – When to use

- **OOMKilled:** the container was killed by the Kubelet for exceeding the memory limit. Common in Java: heap + metaspace + native > limit.
- A **heap dump** is a snapshot of heap memory; used to analyze **memory leaks** (which objects are retaining memory).

### Step 3.2 – How to get a heap dump in K8s

- **While running:** `kubectl exec <pod> -n <namespace> -- jmap -dump:live,format=b,file=/tmp/heap.hprof 1` (requires JDK in the container; file stays inside the pod).
- **On OOM:** some JVMs can auto-generate a heap dump with `-XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/tmp`. The file is on the container filesystem; if the pod restarts, it is lost. In production, a volume or sidecar is sometimes used to copy the dump to storage.

In your environment, check if any deployment has **JVM_OPTIONS** with `HeapDumpOnOutOfMemoryError`; if not, it is an improvement for OOM incidents.

### Step 3.3 – Quick checklist for OOMKilled

- [ ] Run `kubectl describe pod` – exit reason: OOMKilled?
- [ ] Compare container **memory limit** with **-Xmx** (and other JVM memory areas).
- [ ] If possible, collect a heap dump before the next restart (or enable HeapDumpOnOutOfMemoryError for the next event).
- [ ] Adjust heap (lower) or increase memory limit (carefully to avoid exhausting the node).

---

## Part 4 – JVM and GC metrics

### Step 4.1 – Where do metrics show up?

- **Spring Boot Actuator** can expose metrics at `/actuator/prometheus` (Prometheus format).
- **OpenTelemetry** (Java Agent) can export JVM metrics (heap, GC, threads) to the same trace backend (SigNoz/collector).
- In **SigNoz**, dashboards or metrics can show heap usage, GC time, etc., if the collector is configured to receive OTLP metrics.

### Step 4.2 – What to look at in a “slowness” incident

- **GC:** long (stop-the-world) pauses increase latency; metrics like “GC time” or “pause time”.
- **Heap:** usage close to max may mean the JVM is doing GC very often.
- **Threads:** many threads in BLOCKED or RUNNABLE in code holding locks may indicate contention.

**Task:** List three JVM metrics you would check first when investigating “application slow”.

**Example answer:** (1) Heap used vs max, (2) GC pause time (or frequency), (3) Thread count or thread states.

---

## Part 5 – Simulated scenario (summary)

Imagine: an application pod in staging is in **CrashLoopBackOff**.

1. What command would you use to see why it is crashing?
2. What three most common causes would you check (config, Config Server, DB, resources, JVM)?
3. Where would you look for the Config Server endpoint (environment variable, properties in config-properties)?

Answer in short form; use the [02_sre_checklist_java_k8s](../02_sre_checklist_java_k8s.md) checklist as support.

---

## References

- [02_sre_checklist_java_k8s](../02_sre_checklist_java_k8s.md) – Quick troubleshooting
- [01_stack](../01_stack.md) – Observability
- Kubernetes: `kubectl logs`, `kubectl exec`, `kubectl describe pod`

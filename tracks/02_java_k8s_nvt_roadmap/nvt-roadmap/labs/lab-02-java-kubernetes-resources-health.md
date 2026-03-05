# Lab 02 – Java on Kubernetes: resources, JVM and health checks

**Objective:** Configure **resources** (CPU/memory), **JVM options** and **probes** (liveness/readiness) in a Java application Deployment, aligned with the reference environment.

---

## Prerequisites

- Docker installed.
- `kubectl` configured (kind, minikube or OKE dev/staging cluster).
- Lab 01 done (recommended).
- Read [02_sre_checklist_java_k8s](../02_sre_checklist_java_k8s.md) (Resources and Probes sections).

---

## Part 1 – Analyze a real Deployment

### Step 1.1 – Resources and JVM in the application deployment

1. Open the application’s **deployment.yaml** in staging (e.g. `repo-manifests-k8s/k8s/staging/app-manifest/connect/deployment.yaml` in your workspace).
2. Locate:
   - **resources** (requests/limits for CPU and memory).
   - **env** with **JVM_OPTIONS** (including `-Xmx`, `-javaagent`, `Dotel.*`).
3. Answer:
   - What is the memory limit? Is the `-Xmx` value smaller than that limit? (It should be; the JVM uses more than just heap.)
   - Are probes (liveness/readiness) enabled or commented out? If enabled, which path and port?

**Why?** In many environments the pattern is a high limit (e.g. 6Gi) and fixed heap (e.g. 2g); the rest is for metaspace, threads and native. Commented probes mean the team disabled them temporarily; in production you ideally use health/ping.

### Step 1.2 – Heap vs memory limit

- Container memory limit: **6Gi** (staging example).
- `-Xmx2048m` = 2Gi heap.
- Rule of thumb: heap ≈ 70–80% of limit for a “normal” Java app; the rest is metaspace + threads + native.
- If the limit were 2Gi and heap 2Gi, the pod could be **OOMKilled**. Why? (Search “OOMKilled Java container” if needed.)

---

## Part 2 – Practice: minimal Java (Spring Boot) Deployment

Use a public sample image (Spring Boot) or a JAR you already have. The focus here is **resources + JVM + probes**, not code.

### Step 2.1 – Create a test Deployment

Create `lab02-deployment.yaml` (in any working directory):

**Option A – Just test resources (no JAR):** a container that stays running so you can exercise `kubectl` and observe resources/OOMKilled.

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
        args: ["sleep", "3600"]
        resources:
          requests:
            memory: "384Mi"
            cpu: "200m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

**Option B – Real Spring Boot app:** use an image that already has a Spring Boot app. In that case add: `env` with `JAVA_OPTS`, `resources`, and probes pointing to `/actuator/health` port 8080 with suitable `initialDelaySeconds` and `periodSeconds`.

Apply and watch:

```bash
kubectl apply -f lab02-deployment.yaml
kubectl get pods -w
```

### Step 2.2 – Adjust resources and observe

1. Lower the **memory limit** to a small value (e.g. 128Mi) and keep a high heap (e.g. `-Xmx256m`). Apply and watch the pod (it should go OOMKilled).
2. Restore a limit higher than heap (e.g. 512Mi limit, 256m heap) and confirm the pod stays Running.

**Verification:** Can you explain why 128Mi limit with 256m heap leads to OOMKilled?

---

## Part 3 – Probes in the deployment

1. Go back to the application’s **deployment.yaml** in staging.
2. Mentally uncomment (or in a local copy) the **startupProbe**, **livenessProbe** and **readinessProbe** sections.
3. Note:
   - Liveness vs readiness path (health vs ping).
   - Why use **HTTPS** and port **9090** (the application’s port).
   - What happens if `initialDelaySeconds` is too small for a heavy JVM + Spring Boot.

**Optional task:** In a test cluster, create a Deployment with a Java app that exposes `/actuator/health` and set liveness and readiness; force a failure (e.g. bring down the DB) and observe readiness vs liveness behavior.

---

## References

- [02_sre_checklist_java_k8s](../02_sre_checklist_java_k8s.md) – Resources and Probes
- [01_stack](../01_stack.md) – Stack and manifests
- Application deployment.yaml in staging (K8s manifests repo)

# SRE Checklist – Java on Kubernetes

Objective checklist for **operations**, **deploy**, and **troubleshooting** of Java (Spring Boot) applications on Kubernetes, aligned with the reference environment (names and sensitive data generalized).

---

## 1. Before deploy

- [ ] **Config Server** is up and reachable from the cluster (URL, network, DNS).
- [ ] **Properties** for the profile (`CLOUD_PROFILE`) exist in the config-properties repository and are correct (datasource, URLs, feature flags).
- [ ] **Image** was built and pushed to the registry with the tag expected by the manifest.
- [ ] **Secrets** in the cluster: `imagePullSecrets` in the namespace; app secrets (TLS, DB, etc.) if applicable.
- [ ] **Manifests** in the manifests repo are up to date for the environment (image, tag, namespace, resources).

---

## 2. Container resources (Java/JVM)

- [ ] **Memory limit** of the container is greater than the JVM max heap (heap + metaspace + threads + native). Avoid OOMKilled.
- [ ] **JVM:** use `-XX:MaxRAMPercentage` / `-XX:InitialRAMPercentage` (Java 10+) or `-Xmx`/`-Xms` consistent with the limit (e.g. 70–80% of limit for heap).
- [ ] **CPU:** requests/limits set; adjust GC threads if needed on nodes with few cores.
- [ ] **JVM_OPTIONS** in the Deployment include the OpenTelemetry agent and OTLP endpoint when observability is enabled.

---

## 3. Health checks (probes)

- [ ] **Liveness** uses an endpoint that indicates “process alive” (e.g. `/portal/health`); timeout and failureThreshold suitable to avoid kill due to long GC.
- [ ] **Readiness** uses an endpoint that indicates “ready for traffic” (e.g. `/portal/ping` or light dependencies); do not send traffic before the app is ready.
- [ ] **Startup probe** (if present) with enough initialDelaySeconds/period for JVM + Spring Boot to come up (e.g. 180s for heavy apps).
- [ ] Probes do not use an endpoint that depends on a slow external dependency (e.g. DB) for liveness, to avoid cascading restarts.

---

## 4. Config and profile

- [ ] **CLOUD_PROFILE** in the Deployment matches an existing profile in Config Server (e.g. `profile-staging`, `profile-prod-oci`).
- [ ] Sensitive environment variables come from **Secrets** (not hardcoded in the deployment).
- [ ] **Bootstrap** of Config Server (keystore, Git URI) is correct when encryption is used.

---

## 5. Observability

- [ ] **OpenTelemetry:** agent in the image; `JVM_OPTIONS` with `-javaagent` and `Dotel.exporter.otlp.endpoint` pointing to the collector (IP/hostname reachable from the Pod).
- [ ] **SigNoz** (or OTLP backend) receiving data from the cluster (collector/agent configured in cluster-manifest).
- [ ] **Logs:** application logging to stdout (and in a consumable format, e.g. JSON) for the cluster logging stack.
- [ ] **Metrics:** Actuator/Prometheus exposed only internally (not on public Ingress) when applicable.

---

## 6. Quick troubleshooting

- [ ] **Pod not starting:** `kubectl describe pod`, `kubectl logs`; check ImagePullBackOff (registry, imagePullSecrets), CrashLoopBackOff (config, Config Server, DB, JVM/startup).
- [ ] **OOMKilled:** review heap vs memory limit; collect heap dump if policy allows; adjust `-Xmx`/MaxRAMPercentage.
- [ ] **High latency / timeouts:** traces in SigNoz; GC and CPU metrics; check connection pools (DB, HTTP client) and thread pools.
- [ ] **Liveness killing the pod:** increase timeout/failureThreshold or change endpoint; check if GC or startup take longer than the probe.
- [ ] **Config not loading:** Is Config Server reachable? Correct profile? Properties repo updated and reachable by Config Server?
- [ ] **Traces not showing:** Is OTLP endpoint reachable from the Pod? Collector Service in same namespace or correct DNS? Firewall/network policies?

---

## 7. Pipelines and manifests

- [ ] **Pipeline:** build uses the correct Dockerfile (profile/client); image tag aligned with what the deployment expects.
- [ ] **Manifest download:** manifests repo URL (branch/repo) correct; applied file is for the right environment (staging/prod/...).
- [ ] **Post-apply:** `kubectl get pods -n <namespace>`, `kubectl rollout status deployment/<name> -n <namespace>` to confirm rollout.

---

Use this checklist when preparing a deploy, investigating incidents, and reviewing changes to resources or JVM in your environment.

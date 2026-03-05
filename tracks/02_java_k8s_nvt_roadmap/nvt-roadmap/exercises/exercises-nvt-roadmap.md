# Exercises – NVT Roadmap

Practice exercises to consolidate the roadmap chapters and labs. Use the chapters and the [SRE checklist](../02_sre_checklist_java_k8s.md) for reference. Repository and environment names have been generalized.

---

## Block 1 – Environment and deploy flow

1. **Order:** List the correct order (1st to 5th) for: (A) deploy Config Server, (B) create namespace in the cluster, (C) configure properties in the config-properties repo, (D) apply the application deployment to the cluster, (E) push the application image to the registry.

2. **CLOUD_PROFILE:** If the deployment in staging has `CLOUD_PROFILE=profile-staging`, which properties file in the config-properties repo must exist for the application to load config?

3. **Dependency:** Why should the main application not start before the Config Server is healthy?

---

## Block 2 – Java on Kubernetes

4. **Resources:** A container has a memory limit of 2Gi. What can happen if the JVM is configured with `-Xmx2g`? What would you change?

5. **Probes:** What is the difference between livenessProbe and readinessProbe? Why not use an endpoint that depends on the database for liveness?

6. **OOMKilled:** The pod was killed with reason OOMKilled. List three investigation or fix actions.

---

## Block 3 – Observability

7. **OpenTelemetry:** In the deployment, where are the OTLP endpoint and service name (service.name) configured for the Java agent?

8. **SigNoz:** Where in the K8s manifests repo is the SignOz/Otel Collector configuration for the cluster (e.g. cluster-manifest/signoz)?

9. **Traces:** If traces do not appear in SigNoz, list three things you would check (app, network, collector).

---

## Block 4 – Troubleshooting

10. **CrashLoopBackOff:** What commands would you use to find out why a pod is crashing?

11. **Thread dump:** What is a thread dump for, and what kind of problem does it help with most?

12. **Latency:** The application is slow. List three sources of information (metrics, logs, traces) you would use to investigate.

---

## Block 5 – Pipelines and manifests

13. **Pipeline:** In one sentence, what does the deploy pipeline do after pushing the image to the registry?

14. **Manifests:** Why does each environment (staging, prod, etc.) have its own directory in the manifests repo (e.g. k8s/<environment>/)?

15. **Dry-run:** What is `kubectl apply -f deployment.yaml --dry-run=client` useful for?

---

## Suggested answers (try first before looking)

<details>
<summary>Click to see suggested answers</summary>

1. Order: 1st C (properties), 2nd A (Config Server), 3rd B (namespace/infra), 4th E (push image), 5th D (apply deployment).  
2. A file like `connect-profile-staging.properties` must exist (or the name the Config Server builds from application + profile).  
3. Because on startup the application calls the Config Server to get properties; if the Config Server is not reachable, the application fails at bootstrap.  
4. The JVM uses more than just heap (metaspace, threads, native); with 2Gi limit and 2g heap you can get OOMKilled. Reduce heap (e.g. 1g) or increase limit.  
5. Liveness: “process alive”; readiness: “ready for traffic”. If liveness depends on the DB and the DB goes down, the Kubelet kills the pod and makes things worse.  
6. Run describe pod; compare heap with limit; enable HeapDumpOnOOM and analyze dump; adjust -Xmx or limit.  
7. In JVM_OPTIONS: -Dotel.exporter.otlp.endpoint and -Dotel.resource.attributes=service.name=...  
8. K8s manifests repo: cluster-manifest/signoz/k8s-infra/ (values, templates).  
9. Agent in the image; endpoint reachable from the pod; collector running and exporting to SigNoz.  
10. kubectl describe pod; kubectl logs <pod> --previous; kubectl logs <pod>.  
11. Shows the state of all threads; helps with deadlock and blocked threads.  
12. JVM metrics (GC, heap); traces in SigNoz (latency per span); logs (errors, timeouts).  
13. Downloads the deployment (and other manifests) from the K8s manifests repo and applies them to the cluster with kubectl apply.  
14. Because each environment has its own config (image, tag, profile, resources, namespace).  
15. Validates the manifest and shows what would be applied without actually applying to the cluster.

</details>

---

Use these exercises after completing the labs to reinforce the content and as a review before working on deploys or incidents in your environment.

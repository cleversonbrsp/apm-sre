# Checklist SRE – Java no Kubernetes (ambiente NVT)

Checklist objetivo para **operações**, **deploy** e **troubleshooting** de aplicações Java (Spring Boot) no Kubernetes, alinhado ao ambiente de referência (nomes e dados sensíveis generalizados).

---

## 1. Antes do deploy

- [ ] **Config Server** está no ar e acessível a partir do cluster (URL, rede, DNS).
- [ ] **Propriedades** do perfil (`CLOUD_PROFILE`) existem no repositório de config-properties e estão corretas (datasource, URLs, feature flags).
- [ ] **Imagem** foi gerada e enviada ao OCIR com a tag esperada pelo manifesto.
- [ ] **Secrets** no cluster: `imagePullSecrets` (ocirsecret) no namespace; secrets de app (TLS, DB, etc.) se aplicável.
- [ ] **Manifestos** em devops-config estão atualizados para o ambiente (imagem, tag, namespace, recursos).

---

## 2. Recursos do container (Java/JVM)

- [ ] **Memory limit** do container é maior que o heap máximo da JVM (heap + metaspace + threads + nativo). Evitar OOMKilled.
- [ ] **JVM:** uso de `-XX:MaxRAMPercentage` / `-XX:InitialRAMPercentage` (Java 10+) ou `-Xmx`/`-Xms` coerentes com o limit (ex.: 70–80% do limit para heap).
- [ ] **CPU:** requests/limits definidos; ajuste de GC threads se necessário em nós com poucos cores.
- [ ] **JVM_OPTIONS** no Deployment incluem agente OpenTelemetry e endpoint OTLP quando observabilidade estiver ativa.

---

## 3. Health checks (probes)

- [ ] **Liveness** usa endpoint que indica “processo vivo” (ex.: `/portal/health`); timeout e failureThreshold adequados para evitar kill por GC longo.
- [ ] **Readiness** usa endpoint que indica “pronto para tráfego” (ex.: `/portal/ping` ou dependências leves); não enviar tráfego antes do app estar pronto.
- [ ] **Startup probe** (se existir) com initialDelaySeconds/period suficientes para a JVM + Spring Boot subirem (ex.: 180s em apps pesadas).
- [ ] Probes não usam endpoint que dependa de dependência externa lenta (ex.: DB) para liveness, para evitar restart em cascata.

---

## 4. Config e perfil

- [ ] **CLOUD_PROFILE** no Deployment corresponde a um perfil existente no Config Server (ex.: `perfil-hom`, `perfil-prod-oci`).
- [ ] Variáveis de ambiente sensíveis vêm de **Secrets** (não hardcoded no deployment).
- [ ] **Bootstrap** do Config Server (keystore, Git URI) está correto quando há criptografia.

---

## 5. Observabilidade

- [ ] **OpenTelemetry:** agente na imagem; `JVM_OPTIONS` com `-javaagent` e `Dotel.exporter.otlp.endpoint` apontando para o collector (IP/hostname acessível do Pod).
- [ ] **SigNoz** (ou backend OTLP) recebendo dados do cluster (collector/agent configurado no cluster-manifest).
- [ ] **Logs:** aplicação logando em stdout (e em formato consumível, ex.: JSON) para o stack de logging do cluster.
- [ ] **Métricas:** Actuator/Prometheus expostos apenas internamente (não no Ingress público) quando aplicável.

---

## 6. Troubleshooting rápido

- [ ] **Pod não sobe:** `kubectl describe pod`, `kubectl logs`; verificar ImagePullBackOff (OCIR, imagePullSecrets), CrashLoopBackOff (config, Config Server, DB, JVM/startup).
- [ ] **OOMKilled:** revisar heap vs memory limit; coletar heap dump se política permitir; ajustar `-Xmx`/MaxRAMPercentage.
- [ ] **Latência alta / timeouts:** traces no SigNoz; métricas de GC e CPU; verificar pool de conexões (DB, HTTP client) e thread pools.
- [ ] **Liveness matando o pod:** aumentar timeout/failureThreshold ou trocar endpoint; verificar se GC ou startup estão demorando mais que o probe.
- [ ] **Config não carrega:** Config Server acessível? Perfil correto? Repositório de properties atualizado e acessível pelo Config Server?
- [ ] **Traces não aparecem:** endpoint OTLP acessível do Pod? Service do collector no mesmo namespace ou DNS correto? Firewall/network policies?

---

## 7. Pipelines e manifestos

- [ ] **Pipeline:** build usa Dockerfile correto (perfil/cliente); tag de imagem alinhada ao que o deployment espera.
- [ ] **Download de manifestos:** URL do repositório de manifestos (branch/repo) correta; arquivo aplicado é o do ambiente certo (hom/prod/...).
- [ ] **Pós-apply:** `kubectl get pods -n <namespace>`, `kubectl rollout status deployment/<name> -n <namespace>` para confirmar rollout.

---

Use este checklist ao preparar um deploy, ao investigar incidentes e ao revisar mudanças em recursos ou JVM no seu ambiente.

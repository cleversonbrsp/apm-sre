# Exercícios – NVT Roadmap

Exercícios de fixação para consolidar o conteúdo dos capítulos e labs do roadmap. Use os capítulos e o [checklist SRE](../02_sre_checklist_java_k8s.md) como apoio. Nomes de repositórios e ambientes foram generalizados.

---

## Bloco 1 – Ambiente e fluxo de deploy

1. **Ordem:** Liste a ordem correta (1º a 5º) para: (A) deploy do Config Server, (B) criação do namespace no OKE, (C) configuração das properties no repositório config-properties, (D) aplicação do deployment da Connect no cluster, (E) push da imagem da Connect para o OCIR.

2. **CLOUD_PROFILE:** Se o deployment em hom tiver `CLOUD_PROFILE=perfil-hom`, qual arquivo de properties no repositório de config-properties deve existir para a aplicação carregar a config?

3. **Dependência:** Por que a aplicação principal não deve subir antes do Config Server estar saudável?

---

## Bloco 2 – Java no Kubernetes

4. **Recursos:** Um container tem memory limit de 2Gi. O que pode acontecer se a JVM estiver configurada com `-Xmx2g`? O que você mudaria?

5. **Probes:** Qual a diferença entre livenessProbe e readinessProbe? Por que não usar um endpoint que depende do banco de dados para o liveness?

6. **OOMKilled:** O pod foi morto com motivo OOMKilled. Cite três ações de investigação ou correção.

---

## Bloco 3 – Observabilidade

7. **OpenTelemetry:** No deployment, onde são configurados o endpoint OTLP e o nome do serviço (service.name) para o agente Java?

8. **SigNoz:** Onde no repositório de manifestos K8s está a configuração do SignOz/Otel Collector para o cluster (ex.: cluster-manifest/signoz)?

9. **Traces:** Se os traces não aparecem no SigNoz, cite três pontos que você verificaria (app, rede, collector).

---

## Bloco 4 – Troubleshooting

10. **CrashLoopBackOff:** Quais comandos você usaria para descobrir o motivo do crash de um pod?

11. **Thread dump:** Para que serve um thread dump e em que tipo de problema ele mais ajuda?

12. **Latência:** A aplicação está lenta. Cite três fontes de informação (métricas, logs, traces) que você usaria para investigar.

---

## Bloco 5 – Pipelines e manifestos

13. **Pipeline:** Em uma frase, o que o pipeline de deploy faz após o push da imagem para o registry?

14. **Manifestos:** Por que cada ambiente (hom, prod, etc.) tem seu próprio diretório no repositório de manifestos (ex.: k8s/<ambiente>/)?

15. **Dry-run:** Qual a utilidade de `kubectl apply -f deployment.yaml --dry-run=client`?

---

## Respostas sugeridas (não olhe antes de tentar)

<details>
<summary>Clique para ver respostas sugeridas</summary>

1. Ordem: 1º C (properties), 2º A (Config Server), 3º B (namespace/infra), 4º E (push imagem), 5º D (apply deployment).  
2. Deve existir um arquivo como `connect-perfil-hom.properties` (ou o nome que o Config Server monta a partir do application + profile).  
3. Porque na subida a aplicação chama o Config Server para obter as properties; se o Config Server não estiver acessível, a aplicação falha no bootstrap.  
4. A JVM usa mais que só heap (metaspace, threads, nativo); com 2Gi de limit e 2g de heap pode ocorrer OOMKilled. Reduzir heap (ex.: 1g) ou aumentar limit.  
5. Liveness: “processo vivo”; readiness: “pronto para tráfego”. Se liveness depender do DB e o DB cair, o Kubelet mata o pod e piora a situação.  
6. Ver describe pod; comparar heap com limit; habilitar HeapDumpOnOOM e analisar dump; ajustar -Xmx ou limit.  
7. Em JVM_OPTIONS: -Dotel.exporter.otlp.endpoint e -Dotel.resource.attributes=service.name=...  
8. Repositório de manifestos K8s: cluster-manifest/signoz/k8s-infra/ (values, templates).  
9. Agente na imagem; endpoint acessível do pod; collector rodando e exportando para SigNoz.  
10. kubectl describe pod; kubectl logs <pod> --previous; kubectl logs <pod>.  
11. Mostra estado das threads; ajuda em deadlock e threads bloqueadas.  
12. Métricas JVM (GC, heap); traces no SigNoz (latência por span); logs (erros, timeouts).  
13. Baixa o deployment (e outros manifestos) do repositório de manifestos K8s e aplica no cluster com kubectl apply.  
14. Porque cada ambiente tem suas próprias configs (imagem, tag, perfil, recursos, namespace).  
15. Validar o manifesto e ver o que seria aplicado sem aplicar de fato no cluster.

</details>

---

Use estes exercícios após concluir os labs para fixar o conteúdo e como revisão antes de atuar em deploys ou incidentes no seu ambiente.

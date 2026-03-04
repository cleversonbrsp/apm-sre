# Lab 05 – Pipelines e manifestos Kubernetes

**Objetivo:** Entender o **fluxo do pipeline** de deploy (build → push → download de manifestos → apply) e praticar a **leitura e interpretação** de um workflow e de um deployment real no repositório de manifestos K8s.

**Nota:** Nomes de repositórios e caminhos foram generalizados. Use os nomes reais do seu ambiente.

---

## Pré-requisitos

- Acesso ao repositório da aplicação e ao repositório de manifestos K8s.
- Conhecimento básico de YAML e GitHub Actions (ou outro CI).
- Ter feito os [Labs 01](lab-01-deploy-e-config-server.md) e [02](lab-02-java-kubernetes-recursos-health.md).

---

## Parte 1 – Estrutura do pipeline de deploy

### Passo 1.1 – Escolher um workflow

1. Abra a pasta **.github/workflows/** do repositório da aplicação principal.
2. Escolha um workflow de deploy para um ambiente (ex.: pipeline para hom ou prod).
3. Liste as **jobs** ou **steps** principais (em ordem): build, test, build image, push, download manifestos, apply.

### Passo 1.2 – Mapear etapas

Para o workflow escolhido, preencha (ou anote):

| Etapa | O que acontece | Onde no workflow (nome do step ou job) |
|-------|----------------|---------------------------------------|
| 1 | Checkout do código | |
| 2 | Build Maven (ou equivalente) | |
| 3 | Build da imagem Docker | |
| 4 | Push da imagem para o registry | |
| 5 | Download do deployment.yaml do repo de manifestos | |
| 6 | Aplicação no cluster (kubectl apply) | |

**Dica:** Procure por “docker build”, nome do registry, “curl” ou API para baixar manifestos, “kubectl apply”.

### Passo 1.3 – Imagem e tag

- Qual **registry** e **repositório** são usados? (ex.: `<registry>/<tenant>/<imagem>`.)
- De onde vem a **tag** da imagem? (ex.: step de versão ou variável `VERSION`.)
- O **deployment.yaml** baixado referencia essa mesma imagem e tag? (O pipeline pode substituir a tag no YAML antes do apply.)

**Verificação:** Se alguém mudar o nome do arquivo de deployment no repositório de manifestos (ex.: de `deployment.yaml` para `deploy.yaml`), o que precisa ser alterado no pipeline?

---

## Parte 2 – Manifestos no repositório de manifestos K8s

### Passo 2.1 – Organização por ambiente

1. Abra a pasta **k8s/** do repositório de manifestos e liste os diretórios de primeiro nível (hom, prod, etc.).
2. Para o **hom**, entre em **app-manifest/connect/** (ou nome equivalente) e liste os arquivos (deployment, service, hpa, etc.).
3. Abra o **deployment.yaml** do hom e identifique:
   - **namespace** do Deployment.
   - **image** (registry + nome + tag).
   - **CLOUD_PROFILE** e **JVM_OPTIONS** (já vistos no Lab 02).

### Passo 2.2 – Diferenças entre ambientes

Compare o **deployment.yaml** de hom com o de prod (se existir). Anote pelo menos duas diferenças (ex.: número de replicas, recursos, CLOUD_PROFILE, image tag).

**Por quê?** Cada ambiente pode ter recursos, perfis e tags diferentes; o pipeline de cada ambiente baixa o manifesto **do seu** ambiente.

### Passo 2.3 – Cluster-manifest (SignOz, Ingress)

1. Em **k8s/hom/cluster-manifest/** (ou equivalente), liste as pastas (ex.: signoz, ingress, nginx).
2. Na pasta do SignOz (ex.: **cluster-manifest/signoz/k8s-infra/**), abra o **values.yaml** (ou template) e localize a configuração do **endpoint** do Otel Collector ou do SigNoz (ex.: `otelCollectorEndpoint`). Isso é o que as aplicações usam em `OTEL_EXPORTER_OTLP_ENDPOINT`? (Pode ser um Service do cluster.)

---

## Parte 3 – Simular uma alteração segura (dry-run)

**Objetivo:** Praticar alteração em um manifesto **localmente** e ver o que seria aplicado, **sem** aplicar em cluster real.

### Passo 3.1 – Cópia local do deployment

1. Copie o **deployment.yaml** da aplicação em hom para um diretório de trabalho (ex.: `lab05-workspace/deployment.yaml`).
2. Altere **apenas** um valor não crítico, por exemplo:
   - Um **label** no `metadata.labels` (ex.: adicione `lab: lab05`).
   - Ou um **resource request** (ex.: altere `memory: "6Gi"` para `memory: "4Gi"` na cópia).

### Passo 3.2 – Validar e dry-run

- Valide o YAML (sintaxe): use um validador online ou `kubectl apply -f deployment.yaml --dry-run=client -o yaml` (isso não aplica no cluster; só valida e mostra o que seria aplicado).
- Se você tivesse acesso ao cluster hom, o comando real seria algo como: `kubectl apply -f deployment.yaml -n hom --dry-run=server` (valida no servidor sem aplicar).

**Verificação:** Qual a diferença entre `--dry-run=client` e `--dry-run=server`? (Pesquise na documentação do kubectl.)

---

## Parte 4 – Ordem de apply em um deploy completo

Ao fazer um deploy “do zero” ou em um novo ambiente, em que ordem você aplicaria os recursos? (Use o documento de procedimento e o Lab 01.)

1. Namespace (se não existir).
2. Secrets (imagePullSecrets, etc.).
3. ConfigMaps (se houver).
4. Deployment (e depois Service, HPA, Ingress conforme o processo do time).

**Tarefa opcional:** No pipeline da aplicação, existe aplicação de **Service** e **HPA** além do Deployment? Se sim, em quais steps e em que ordem?

---

## Referências

- [00_visao_geral_ambiente](../00_visao_geral_ambiente.md) – Fluxo de deploy
- [01_stack_nvt](../01_stack_nvt.md) – Pipelines e manifestos
- Documento de procedimento de deploy (repositório de trabalho)
- .github/workflows/ do repositório da aplicação
- k8s/ do repositório de manifestos K8s

# Lab 01 – Fluxo de deploy e Config Server

**Objetivo:** Entender a **ordem das dependências** do deploy e localizar onde cada peça é configurada (config-properties, Config Server, manifestos, pipelines).

**Nota:** Caminhos e nomes de repositórios foram generalizados para não expor a empresa. Use os nomes reais do seu ambiente.

---

## Pré-requisitos

- Acesso ao repositório de trabalho (clone local).
- Leitura dos capítulos [00_visao_geral_ambiente](../00_visao_geral_ambiente.md) e [01_stack_nvt](../01_stack_nvt.md).
- Opcional: documento de procedimento de deploy na raiz do repositório (ordem de configuração, arquivos por etapa).

---

## Parte 1 – Ordem de configuração (teoria + mapeamento)

### Passo 1.1 – Listar a ordem oficial

1. Abra o **documento de procedimento de deploy** do seu ambiente (na raiz do repositório de trabalho ou no local indicado pela equipe).
2. Localize a seção de **ordem de configuração** (tabela com 1º a 8º ou equivalente).
3. Anote a ordem resumida:
   - 1º: …
   - 2º: …
   - até o último passo.

**Por quê?** No dia a dia, falhas de deploy costumam vir de algo que não foi configurado na ordem certa (ex.: subir a aplicação antes do Config Server).

### Passo 1.2 – Mapear arquivos reais

Para cada item da tabela, localize **um** arquivo ou pasta correspondente no repositório de trabalho:

| Ordem | O que configurar        | Caminho de exemplo (use os nomes do seu repo) |
|-------|-------------------------|-----------------------------------------------|
| 1º    | Properties da aplicação | `config-properties/` – liste os arquivos `*.properties`. |
| 2º    | Config Server           | `config-server/` – onde está o `application.properties` com Git URI? |
| 3º    | Infra (cluster, registry)| (Fora do repo – anote “cluster, registry, compartment”). |
| 4º    | Manifestos K8s          | `repo-manifestos-k8s/k8s/hom/app-manifest/connect/` – liste os arquivos. |
| 5º    | Artefatos de build      | `repo-infra/` – onde está o `opentelemetry-javaagent.jar`? |
| 6º    | Credenciais             | (Secrets do CI, imagePullSecrets – anote “secrets”). |
| 7º    | Cluster pronto          | (Namespaces, Ingress – anote “cluster-manifest”). |
| 8º    | Código e pipeline       | `app-connect/.github/workflows/` – liste um workflow de deploy. |

Preencha com os caminhos reais do seu ambiente.

**Verificação:** Você consegue explicar por que o Config Server deve estar no “2º” e a aplicação principal no “8º”?

---

## Parte 2 – Config Server e propriedades

### Passo 2.1 – Estrutura do repositório de properties

1. Entre no repositório de **config-properties** (nome real do seu ambiente).
2. Liste os arquivos que definem perfis da aplicação (ex.: `connect.properties`, `connect-perfil-hom.properties`).
3. Abra um arquivo de perfil e identifique:
   - Uma propriedade de **datasource** (URL, usuário).
   - Uma propriedade de **URL do Config Server** ou de outro serviço (se houver).

**Por quê?** A aplicação **não** embute essas configs na imagem; ela as busca no Config Server usando o perfil (`CLOUD_PROFILE`).

### Passo 2.2 – Como a aplicação sabe qual perfil usar?

1. Abra o **deployment.yaml** da aplicação em hom (ex.: `repo-manifestos-k8s/k8s/hom/app-manifest/connect/deployment.yaml`).
2. Procure a variável de ambiente **CLOUD_PROFILE**.
3. Confira: o valor (ex.: `perfil-hom`) deve existir como sufixo em um arquivo no config-properties (ex.: `connect-perfil-hom.properties`).

**Verificação:** Se você mudar `CLOUD_PROFILE` para um valor que não existe no repositório de properties, o que tende a acontecer na subida do pod?

---

## Parte 3 – Resumo do fluxo (deploy)

Desenhe ou escreva em 4 linhas o fluxo:

1. Onde as **configurações** ficam (repositório).
2. Quem **serve** essas configurações em runtime (serviço).
3. Onde a **imagem** da aplicação é publicada (registry).
4. Onde os **manifestos** que rodam a aplicação ficam (repositório + cluster).

**Tarefa opcional:** Abra um workflow de deploy (ex.: pipeline para hom) e identifique, em ordem: etapa de build da imagem, push para o registry, download do deployment, `kubectl apply`.

---

## Referências

- [00_visao_geral_ambiente](../00_visao_geral_ambiente.md)
- [01_stack_nvt](../01_stack_nvt.md)
- Documento de procedimento de deploy (repositório de trabalho)

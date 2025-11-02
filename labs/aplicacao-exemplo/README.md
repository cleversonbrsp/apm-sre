# 🎯 Aplicações de Exemplo Instrumentadas para SigNoz

Este diretório contém aplicações de exemplo totalmente instrumentadas para enviar logs, métricas e traces para o SigNoz.

## 📋 Índice

- [Node.js + Express](#nodejs--express)
- [Python + Flask](#python--flask)
- [Conceitos de Instrumentação](#conceitos-de-instrumentação)
- [Como Funciona](#como-funciona)

---

## 🟢 Node.js + Express

### Estrutura da Aplicação

```
app-nodejs/
├── package.json          # Dependências
├── server.js             # Aplicação principal
├── instrumentation.js    # ⚡ Instrumentação do OpenTelemetry
├── routes/
│   └── api.js           # Rotas da API
└── README.md            # Instruções específicas
```

### Como Executar

```bash
cd app-nodejs
npm install
npm start
```

A aplicação estará rodando em: http://localhost:3000

**Endpoints disponíveis:**
- `GET /api/health` - Health check
- `GET /api/users` - Lista usuários
- `GET /api/users/:id` - Busca usuário específico
- `POST /api/users` - Cria novo usuário
- `GET /api/products` - Lista produtos (simula erro)
- `GET /api/slow` - Endpoint lento (para mostrar métricas)

---

## 🐍 Python + Flask

### Estrutura da Aplicação

```
app-python/
├── requirements.txt      # Dependências Python
├── app.py                # Aplicação principal
├── instrumentation.py    # ⚡ Instrumentação do OpenTelemetry
├── routes/
│   └── api.py           # Rotas da API
└── README.md            # Instruções específicas
```

### Como Executar

```bash
cd app-python
pip install -r requirements.txt
python app.py
```

A aplicação estará rodando em: http://localhost:5000

**Endpoints disponíveis:**
- `GET /api/health` - Health check
- `GET /api/users` - Lista usuários
- `GET /api/users/<id>` - Busca usuário específico
- `POST /api/users` - Cria novo usuário
- `GET /api/random-error` - Gera erro aleatório
- `GET /api/slow` - Endpoint lento

---

## 📚 Conceitos de Instrumentação

### 1. OpenTelemetry (OTEL)

**O que é?** Framework padronizado para coletar dados de telemetria (logs, métricas, traces) de aplicações.

**Componentes principais:**
- **Instrumentation**: Código que coleta dados da sua aplicação
- **Exporters**: Envia dados para backends (como SigNoz)
- **Collector**: Recebe e processa dados (Otel Collector)
- **SDKs**: Bibliotecas para cada linguagem

### 2. Três Pilares da Observabilidade

#### 📊 **LOGS**
- **O que são**: Eventos que acontecem na aplicação
- **Quando usar**: Debug, auditoria, rastreamento de fluxo
- **Exemplo**: "Usuário criado", "Erro ao processar pagamento"

#### 📈 **MÉTRICAS**
- **O que são**: Valores numéricos medidos ao longo do tempo
- **Quando usar**: Performance, saúde da aplicação
- **Exemplo**: Requisições por segundo, tempo de resposta, uso de CPU

#### 🔍 **TRACES**
- **O que são**: Request único através de múltiplos serviços
- **Quando usar**: Debug de problemas em sistemas distribuídos
- **Exemplo**: Trace de uma requisição HTTP através de API, DB, cache

### 3. Como as Dados Fluem

```
┌─────────────────┐
│  Sua Aplicação  │
│   (Node/Python) │
└────────┬────────┘
         │
         │ 1. Dados gerados pelo OpenTelemetry SDK
         ▼
┌──────────────────────────┐
│  Otel Collector          │
│  (porta 4317 ou 4318)    │
└────────┬─────────────────┘
         │
         │ 2. Processa e envia dados
         ▼
┌──────────────────────────┐
│  ClickHouse              │
│  (Banco de dados)        │
└────────┬─────────────────┘
         │
         │ 3. Armazena dados
         ▼
┌──────────────────────────┐
│  SigNoz Frontend         │
│  (Visualização)          │
└──────────────────────────┘
```

---

## 🔧 Como Funciona

### Passo 1: Instalar OpenTelemetry

**Node.js:**
```javascript
npm install @opentelemetry/api
npm install @opentelemetry/sdk-node
npm install @opentelemetry/exporter-otlp-grpc
// Auto-instrumentação para bibliotecas populares
npm install @opentelemetry/instrumentation-http
npm install @opentelemetry/instrumentation-express
```

**Python:**
```python
pip install opentelemetry-api
pip install opentelemetry-sdk
pip install opentelemetry-exporter-otlp-proto-grpc
# Auto-instrumentação
pip install opentelemetry-instrumentation-flask
pip install opentelemetry-instrumentation-requests
```

### Passo 2: Configurar o SDK

O OpenTelemetry SDK precisa saber:
1. **Onde enviar os dados**: Endpoint do Otel Collector
2. **Quais dados coletar**: Logs, métricas, traces
3. **Como estruturar**: Atributos, contexto

### Passo 3: Auto-instrumentação

Mágica! O OpenTelemetry pode instrumentar automaticamente:
- ✅ Biblioteca HTTP
- ✅ Framework web (Express, Flask)
- ✅ Chamadas de banco de dados
- ✅ Redis
- ✅ Kafka
- ✅ E muitas outras!

Sem precisar modificar seu código!

### Passo 4: Enviar Dados

Os dados são enviados automaticamente para:
- **Endpoint**: `http://localhost:4317` (gRPC)
- **Protocolo**: OTLP (OpenTelemetry Protocol)
- **Formato**: gRPC

---

## 🎓 Próximos Passos

1. ✅ Execute as aplicações de exemplo
2. ✅ Acesse http://localhost:8080 para ver os dados no SigNoz
3. ✅ Explore Traces, Métricas e Logs
4. 🔧 Adapte a instrumentação para suas aplicações
5. 📚 Leia a [documentação oficial](https://signoz.io/docs/)

## 📖 Recursos Adicionais

- [OpenTelemetry Docs](https://opentelemetry.io/docs/)
- [SigNoz Instrumentation Guide](https://signoz.io/docs/instrumentation/)
- [OTLP Protocol](https://opentelemetry.io/docs/specs/otlp/)


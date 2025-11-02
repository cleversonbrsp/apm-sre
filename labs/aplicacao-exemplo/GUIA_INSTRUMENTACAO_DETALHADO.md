# 🔧 Guia Detalhado: Como Instrumentar Aplicações

Este guia explica **passo a passo** como instrumentar suas aplicações para enviar dados ao SigNoz.

---

## 📋 Índice

1. [O Que é Instrumentação?](#o-que-é-instrumentação)
2. [Arquitetura de Observabilidade](#arquitetura-de-observabilidade)
3. [Passo a Passo: Node.js](#passo-a-passo-nodejs)
4. [Passo a Passo: Python](#passo-a-passo-python)
5. [Como Funciona na Prática](#como-funciona-na-prática)
6. [Instrumentação Manual vs Automática](#instrumentação-manual-vs-automática)
7. [Adaptando para Sua Aplicação](#adaptando-para-sua-aplicação)

---

## O Que é Instrumentação?

**Instrumentação** é o processo de adicionar código à sua aplicação para coletar dados de telemetria (traces, métricas e logs).

### 🎯 Analogia Simples

Imagine sua aplicação como um carro:

- **Sem instrumentação**: Carro sem painel. Você dirige, mas não sabe velocidade, temperatura, combustível.
- **Com instrumentação**: Carro com painel completo. Você vê tudo que está acontecendo em tempo real.

### 📊 Tipos de Dados Coletados

1. **TRACES** 🔍
   - O que é: Rastreamento de uma requisição do início ao fim
   - Quando usar: "Por que essa requisição está lenta?"
   - Exemplo: Request HTTP → Consulta DB → Chamada API externa → Response

2. **MÉTRICAS** 📈
   - O que é: Valores numéricos ao longo do tempo
   - Quando usar: "Quantas requisições por segundo?"
   - Exemplo: Latência média, taxa de erro, uso de memória

3. **LOGS** 📝
   - O que é: Eventos que acontecem na aplicação
   - Quando usar: "O que aconteceu antes do erro?"
   - Exemplo: "Usuário criado", "Erro ao conectar no DB"

---

## Arquitetura de Observabilidade

```
┌──────────────────────────────────────────────────────────────────┐
│ SUA APLICAÇÃO                                                    │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐     │
│  │ 1. Seu Código (Express, Flask, etc)                    │     │
│  └────────────┬───────────────────────────────────────────┘     │
│               │                                                  │
│  ┌────────────▼───────────────────────────────────────────┐     │
│  │ 2. OpenTelemetry SDK                                   │     │
│  │    - Auto-instrumenta bibliotecas (HTTP, DB, etc)      │     │
│  │    - Coleta traces, métricas, logs                     │     │
│  │    - Adiciona contexto (IDs, atributos)                │     │
│  └────────────┬───────────────────────────────────────────┘     │
└───────────────┼──────────────────────────────────────────────────┘
                │
                │ 3. Envia dados via OTLP (OpenTelemetry Protocol)
                ▼
┌──────────────────────────────────────────────────────────────────┐
│ OTEL COLLECTOR (porta 4317)                                      │
│  - Recebe dados de múltiplas aplicações                          │
│  - Processa e filtra                                             │
│  - Envia para backends                                           │
└────────────┬─────────────────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────────────────┐
│ CLICKHOUSE (Banco de Dados)                                      │
│  - Armazena traces, métricas, logs                               │
└────────────┬─────────────────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────────────────┐
│ SIGNOZ UI (porta 8080)                                           │
│  - Visualiza dados                                               │
│  - Dashboards, alertas, análises                                 │
└──────────────────────────────────────────────────────────────────┘
```

---

## Passo a Passo: Node.js

### 🗂️ Estrutura de Arquivos

```
seu-projeto/
├── package.json          ← 1. Adicionar dependências aqui
├── instrumentation.js    ← 2. CRIAR este arquivo (configuração)
├── server.js             ← 3. Seu código existente
└── node_modules/         ← 4. npm install cria isto
```

### 📍 PASSO 1: Adicionar Dependências

**ONDE:** `package.json`

**O QUE FAZER:** Adicionar as bibliotecas OpenTelemetry

```json
{
  "dependencies": {
    "express": "^4.18.2",
    "@opentelemetry/api": "^1.4.1",
    "@opentelemetry/auto-instrumentations-node": "^0.39.4",
    "@opentelemetry/exporter-trace-otlp-grpc": "^0.41.2",
    "@opentelemetry/resources": "^1.15.2",
    "@opentelemetry/sdk-node": "^0.41.2",
    "@opentelemetry/semantic-conventions": "^1.15.2"
  }
}
```

**EXECUTAR:**
```bash
npm install
```

**O QUE CADA BIBLIOTECA FAZ:**

| Biblioteca | Função |
|-----------|---------|
| `@opentelemetry/api` | API base do OpenTelemetry |
| `@opentelemetry/sdk-node` | SDK para Node.js (motor principal) |
| `@opentelemetry/auto-instrumentations-node` | 🔥 Auto-instrumenta Express, HTTP, etc |
| `@opentelemetry/exporter-trace-otlp-grpc` | Envia traces para SigNoz |
| `@opentelemetry/resources` | Define metadados da aplicação |
| `@opentelemetry/semantic-conventions` | Padrões de nomenclatura |

---

### 📍 PASSO 2: Criar Arquivo de Instrumentação

**ONDE:** Criar arquivo `instrumentation.js` **na raiz do projeto**

**O QUE FAZER:** Configurar o OpenTelemetry SDK

```javascript
// instrumentation.js
const { NodeSDK } = require('@opentelemetry/sdk-node');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-grpc');
const { Resource } = require('@opentelemetry/resources');
const { SemanticResourceAttributes } = require('@opentelemetry/semantic-conventions');

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// PASSO 2.1: Definir Recurso (identifica sua aplicação)
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
const resource = new Resource({
  [SemanticResourceAttributes.SERVICE_NAME]: 'minha-aplicacao',  // ← MUDE AQUI
  [SemanticResourceAttributes.SERVICE_VERSION]: '1.0.0',
  [SemanticResourceAttributes.DEPLOYMENT_ENVIRONMENT]: 'production',
});

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// PASSO 2.2: Configurar Exportador de Traces
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
const traceExporter = new OTLPTraceExporter({
  url: 'http://localhost:4317',  // ← Endpoint do Otel Collector
  // Se o Collector estiver em outro servidor:
  // url: 'http://SEU_SERVIDOR:4317',
});

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// PASSO 2.3: Configurar SDK
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
const sdk = new NodeSDK({
  resource: resource,
  traceExporter: traceExporter,
  
  // 🔥 MAGIA ACONTECE AQUI: Auto-instrumentação
  instrumentations: [
    getNodeAutoInstrumentations({
      // Desabilitar instrumentações que não precisa
      '@opentelemetry/instrumentation-fs': {
        enabled: false,  // Filesystem geralmente não é útil
      },
    }),
  ],
});

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// PASSO 2.4: Inicializar SDK
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
sdk.start();
console.log('⚡ OpenTelemetry iniciado');

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// PASSO 2.5: Shutdown gracioso
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
process.on('SIGTERM', () => {
  sdk.shutdown()
    .then(() => console.log('🔌 Telemetria encerrada'))
    .finally(() => process.exit(0));
});
```

**EXPLICAÇÃO LINHA POR LINHA:**

```javascript
const resource = new Resource({...});
```
- **O que faz:** Cria metadados sobre sua aplicação
- **Por que:** SigNoz usa isso para identificar de onde vêm os dados
- **Mude aqui:** `SERVICE_NAME` para o nome da sua aplicação

```javascript
const traceExporter = new OTLPTraceExporter({...});
```
- **O que faz:** Define ONDE enviar os traces
- **Por que:** Conecta sua app ao Otel Collector
- **Mude aqui:** `url` se o Collector estiver em outro servidor

```javascript
instrumentations: [getNodeAutoInstrumentations()]
```
- **O que faz:** Ativa instrumentação automática
- **Por que:** Rastreia HTTP, Express, DB automaticamente SEM modificar seu código
- **Mude aqui:** Desabilite instrumentações que não usa

```javascript
sdk.start();
```
- **O que faz:** INICIA a coleta de dados
- **Por que:** A partir daqui, TUDO é rastreado!

---

### 📍 PASSO 3: Carregar Instrumentação ANTES da Aplicação

**ONDE:** `package.json` → scripts

**O QUE FAZER:** Usar `-r` (require) para carregar instrumentação primeiro

```json
{
  "scripts": {
    "start": "node -r ./instrumentation.js server.js"
  }
}
```

**EXPLICAÇÃO:**

```
node -r ./instrumentation.js server.js
     ↑                        ↑
     |                        |
  Carrega ANTES           Sua aplicação
```

**ORDEM IMPORTANTÍSSIMA:**

1. ✅ `instrumentation.js` carrega PRIMEIRO
2. ✅ OpenTelemetry se configura
3. ✅ Auto-instrumentação se ativa
4. ✅ `server.js` carrega (já instrumentado!)

**❌ SE CARREGAR NA ORDEM ERRADA:**
```javascript
// ❌ ERRADO - Não funciona!
const express = require('express');  // Carregou Express primeiro
require('./instrumentation');        // Tarde demais!
```

**✅ ORDEM CORRETA:**
```bash
node -r ./instrumentation.js server.js
# Instrumentação carrega ANTES do Express!
```

---

### 📍 PASSO 4: Seu Código NÃO Muda!

**ONDE:** `server.js` (sua aplicação)

**O QUE FAZER:** NADA! Continue programando normalmente!

```javascript
// server.js - SEM MODIFICAÇÕES!
const express = require('express');
const app = express();

app.get('/users', (req, res) => {
  // Seu código normal
  res.json({ users: [] });
});

app.listen(3000);
```

**🎉 MÁGICA:** Mesmo sem modificar nada, o OpenTelemetry já está:
- ✅ Rastreando todas as requisições HTTP
- ✅ Medindo latência
- ✅ Capturando erros
- ✅ Enviando dados para SigNoz

---

### 📍 PASSO 5: Executar e Verificar

**EXECUTAR:**
```bash
npm start
```

**VOCÊ VERÁ:**
```
⚡ OpenTelemetry iniciado
Servidor rodando na porta 3000
```

**TESTAR:**
```bash
curl http://localhost:3000/users
```

**VERIFICAR NO SIGNOZ:**
1. Acesse: http://localhost:8080
2. Vá em "Traces"
3. Veja o trace da requisição `GET /users`!

---

## Passo a Passo: Python

### 🗂️ Estrutura de Arquivos

```
seu-projeto/
├── requirements.txt      ← 1. Adicionar dependências aqui
├── instrumentation.py    ← 2. CRIAR este arquivo
├── app.py                ← 3. Seu código existente
└── venv/                 ← 4. pip install cria isto
```

### 📍 PASSO 1: Adicionar Dependências

**ONDE:** `requirements.txt`

**O QUE FAZER:**
```txt
Flask==3.0.0
opentelemetry-api==1.21.0
opentelemetry-sdk==1.21.0
opentelemetry-exporter-otlp-proto-grpc==1.21.0
opentelemetry-instrumentation-flask==0.42b0
opentelemetry-instrumentation-requests==0.42b0
```

**EXECUTAR:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

### 📍 PASSO 2: Criar Arquivo de Instrumentação

**ONDE:** Criar arquivo `instrumentation.py` **na raiz do projeto**

**O QUE FAZER:**

```python
# instrumentation.py
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PASSO 2.1: Definir Recurso
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
resource = Resource.create({
    SERVICE_NAME: "minha-aplicacao-python",  # ← MUDE AQUI
    SERVICE_VERSION: "1.0.0",
})

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PASSO 2.2: Configurar Provider de Traces
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
tracer_provider = TracerProvider(resource=resource)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PASSO 2.3: Configurar Exportador
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
otlp_exporter = OTLPSpanExporter(
    endpoint="http://localhost:4317",  # ← Endpoint do Collector
    insecure=True,
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PASSO 2.4: Adicionar Processador de Spans
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
span_processor = BatchSpanProcessor(otlp_exporter)
tracer_provider.add_span_processor(span_processor)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PASSO 2.5: Ativar Provider
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
trace.set_tracer_provider(tracer_provider)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PASSO 2.6: Auto-instrumentar Flask e Requests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FlaskInstrumentor().instrument()     # 🔥 Instrumenta Flask
RequestsInstrumentor().instrument()  # 🔥 Instrumenta HTTP requests

print("⚡ OpenTelemetry iniciado")
```

---

### 📍 PASSO 3: Importar ANTES do Flask

**ONDE:** `app.py` (primeira linha!)

**O QUE FAZER:**

```python
# app.py
import instrumentation  # ← PRIMEIRA LINHA! ANTES DO FLASK!

from flask import Flask  # ← Agora sim, Flask

app = Flask(__name__)

@app.route('/users')
def get_users():
    return {'users': []}

if __name__ == '__main__':
    app.run(port=5000)
```

**ORDEM IMPORTANTÍSSIMA:**

```python
# ✅ CORRETO
import instrumentation  # 1. Instrumentação PRIMEIRO
from flask import Flask # 2. Flask DEPOIS

# ❌ ERRADO
from flask import Flask       # Flask primeiro
import instrumentation        # Tarde demais!
```

---

### 📍 PASSO 4: Executar e Verificar

**EXECUTAR:**
```bash
python app.py
```

**TESTAR:**
```bash
curl http://localhost:5000/users
```

**VERIFICAR NO SIGNOZ:**
- Acesse http://localhost:8080
- Veja os traces!

---

## Como Funciona na Prática

### 🔄 Fluxo Completo de um Request

```
1. Request chega
   └─→ GET /users
       │
2. OpenTelemetry cria TRACE
   └─→ Trace ID: abc123...
       │
3. OpenTelemetry cria SPAN para request HTTP
   └─→ Span: "GET /users"
       ├─ http.method: GET
       ├─ http.route: /users
       ├─ http.status_code: 200
       └─ duration: 45ms
       │
4. Seu código executa (instrumentado automaticamente)
   └─→ Se chamar DB, cria outro SPAN
       └─→ Span: "SELECT * FROM users"
           └─ duration: 30ms
       │
5. Response enviada
   └─→ Span finalizado
       │
6. Dados enviados para Otel Collector
   └─→ OTLP gRPC → localhost:4317
       │
7. Collector processa e envia para ClickHouse
   └─→ Dados armazenados
       │
8. SigNoz UI mostra o trace
   └─→ Você vê no dashboard!
```

### 📊 O Que Você Vê no SigNoz

**Trace completo:**
```
GET /users                     [200] 45ms
├─ express.middleware          5ms
├─ express.request_handler     40ms
│  └─ db.query                 30ms
│     └─ SELECT * FROM users
└─ express.response            < 1ms
```

---

## Instrumentação Manual vs Automática

### 🤖 Auto-Instrumentação (Recomendado)

**O que é:** OpenTelemetry instrumenta bibliotecas automaticamente

**Vantagens:**
- ✅ Não precisa modificar código
- ✅ Cobre casos comuns (HTTP, DB, cache)
- ✅ Rápido de implementar

**Bibliotecas suportadas:**
- HTTP/HTTPS
- Express, Koa, Fastify (Node.js)
- Flask, Django, FastAPI (Python)
- PostgreSQL, MySQL, MongoDB
- Redis, Memcached
- GraphQL
- gRPC

### ✋ Instrumentação Manual

**Quando usar:** Para operações específicas do seu negócio

**Exemplo Node.js:**
```javascript
const { trace } = require('@opentelemetry/api');

app.get('/process-payment', async (req, res) => {
  const tracer = trace.getTracer('minha-app');
  
  // Criar span customizado
  const span = tracer.startSpan('processar_pagamento');
  
  try {
    // Adicionar atributos customizados
    span.setAttribute('payment.amount', 100.00);
    span.setAttribute('payment.currency', 'BRL');
    span.setAttribute('user.id', '123');
    
    // Sua lógica
    await processPayment();
    
    span.setStatus({ code: SpanStatusCode.OK });
  } catch (error) {
    span.setStatus({ 
      code: SpanStatusCode.ERROR,
      message: error.message 
    });
    throw error;
  } finally {
    span.end();  // SEMPRE finalizar!
  }
  
  res.json({ status: 'ok' });
});
```

**Exemplo Python:**
```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

@app.route('/process-payment')
def process_payment():
    # Criar span customizado
    with tracer.start_as_current_span("processar_pagamento") as span:
        # Adicionar atributos
        span.set_attribute("payment.amount", 100.00)
        span.set_attribute("payment.currency", "BRL")
        
        # Sua lógica
        result = process_payment_logic()
        
        return {'status': 'ok'}
```

---

## Adaptando para Sua Aplicação

### ✅ Checklist de Instrumentação

1. **Identificar stack tecnológico**
   - [ ] Linguagem: Node.js, Python, Go, Java?
   - [ ] Framework: Express, Flask, Spring?
   - [ ] Banco de dados: PostgreSQL, MongoDB?
   - [ ] Cache: Redis, Memcached?

2. **Instalar dependências**
   - [ ] SDK OpenTelemetry
   - [ ] Auto-instrumentações para seu stack
   - [ ] Exportador OTLP

3. **Criar instrumentation file**
   - [ ] Configurar recurso (SERVICE_NAME)
   - [ ] Configurar exportador (endpoint)
   - [ ] Habilitar auto-instrumentações

4. **Carregar ANTES da aplicação**
   - [ ] Node.js: `-r ./instrumentation.js`
   - [ ] Python: `import instrumentation` (primeira linha)

5. **Testar**
   - [ ] Executar aplicação
   - [ ] Fazer requests
   - [ ] Ver traces no SigNoz

### 🎯 Onde Instrumentar?

**Prioridades:**

1. **Alta prioridade (sempre instrumentar):**
   - ✅ Requisições HTTP/API
   - ✅ Chamadas de banco de dados
   - ✅ Operações de cache
   - ✅ Chamadas a APIs externas

2. **Média prioridade:**
   - ⚡ Processamento de filas (RabbitMQ, Kafka)
   - ⚡ Uploads/downloads de arquivos
   - ⚡ Operações de autenticação

3. **Baixa prioridade (instrumentar se necessário):**
   - 📝 Operações de filesystem
   - 📝 Cálculos internos
   - 📝 Manipulação de strings

### 📝 Exemplo Completo Real

```javascript
// instrumentation.js (mesmo para qualquer app Node.js)
const { NodeSDK } = require('@opentelemetry/sdk-node');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-grpc');
const { Resource } = require('@opentelemetry/resources');
const { SemanticResourceAttributes } = require('@opentelemetry/semantic-conventions');

const sdk = new NodeSDK({
  resource: new Resource({
    [SemanticResourceAttributes.SERVICE_NAME]: process.env.SERVICE_NAME || 'my-service',
    [SemanticResourceAttributes.SERVICE_VERSION]: process.env.npm_package_version || '1.0.0',
    [SemanticResourceAttributes.DEPLOYMENT_ENVIRONMENT]: process.env.NODE_ENV || 'development',
  }),
  traceExporter: new OTLPTraceExporter({
    url: process.env.OTEL_EXPORTER_OTLP_ENDPOINT || 'http://localhost:4317',
  }),
  instrumentations: [getNodeAutoInstrumentations()],
});

sdk.start();
process.on('SIGTERM', () => sdk.shutdown());
```

Agora pode usar em QUALQUER aplicação Node.js! 🚀

---

## 📚 Resumo

1. **Instalar** dependências OpenTelemetry
2. **Criar** arquivo `instrumentation.js/py`
3. **Configurar** recurso e exportador
4. **Carregar ANTES** da aplicação
5. **Pronto!** Tudo instrumentado automaticamente

**A mágica é:** Você NÃO precisa modificar seu código! 🎉


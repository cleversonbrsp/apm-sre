# ⚡ Parte 2: Adicionando Instrumentação

**Objetivo:** Adicionar OpenTelemetry na aplicação que você criou!

---

## 🎯 O Que Você Vai Fazer

1. Instalar dependências OpenTelemetry
2. Criar arquivo de instrumentação
3. Configurar exportador
4. Carregar instrumentação antes da aplicação
5. Ver traces no SigNoz! 🎉

---

## 🟢 Node.js

### Passo 2.1: Instalar Dependências

```bash
cd meu-projeto-nodejs

npm install @opentelemetry/api \
            @opentelemetry/sdk-node \
            @opentelemetry/auto-instrumentations-node \
            @opentelemetry/exporter-trace-otlp-grpc \
            @opentelemetry/resources \
            @opentelemetry/semantic-conventions
```

**Aguarde a instalação... (pode demorar 1-2 minutos)**

### Passo 2.2: Criar Arquivo de Instrumentação

Crie o arquivo `instrumentation.js` **NA MESMA PASTA que app.js**:

```javascript
// instrumentation.js
const { NodeSDK } = require('@opentelemetry/sdk-node');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-grpc');
const { Resource } = require('@opentelemetry/resources');
const { SemanticResourceAttributes } = require('@opentelemetry/semantic-conventions');

console.log('🔧 Configurando OpenTelemetry...');

// PASSO 1: Definir recurso (metadados da aplicação)
const resource = new Resource({
  [SemanticResourceAttributes.SERVICE_NAME]: 'meu-todo-app',
  [SemanticResourceAttributes.SERVICE_VERSION]: '1.0.0',
  [SemanticResourceAttributes.DEPLOYMENT_ENVIRONMENT]: 'development',
});

// PASSO 2: Configurar exportador de traces
const traceExporter = new OTLPTraceExporter({
  url: 'http://localhost:4317',  // Otel Collector
});

// PASSO 3: Criar e configurar SDK
const sdk = new NodeSDK({
  resource: resource,
  traceExporter: traceExporter,
  instrumentations: [
    getNodeAutoInstrumentations({
      // Desabilita filesystem (não é útil para esta app)
      '@opentelemetry/instrumentation-fs': {
        enabled: false,
      },
    }),
  ],
});

// PASSO 4: Inicializar!
sdk.start();
console.log('⚡ OpenTelemetry iniciado!');
console.log('📊 Enviando traces para: http://localhost:4317');
console.log('🔍 Veja os dados em: http://localhost:8080\n');

// PASSO 5: Shutdown gracioso
process.on('SIGTERM', () => {
  sdk.shutdown()
    .then(() => console.log('🔌 Telemetria encerrada'))
    .finally(() => process.exit(0));
});
```

### Passo 2.3: Modificar package.json

Edite o arquivo `package.json` e adicione o script:

```json
{
  "scripts": {
    "start": "node -r ./instrumentation.js app.js"
  }
}
```

**IMPORTANTE:** O `-r` carrega `instrumentation.js` ANTES de `app.js`!

### Passo 2.4: Executar com Instrumentação

```bash
npm start
```

Você verá:

```
🔧 Configurando OpenTelemetry...
⚡ OpenTelemetry iniciado!
📊 Enviando traces para: http://localhost:4317
🔍 Veja os dados em: http://localhost:8080

🚀 Servidor rodando em http://localhost:3001
```

### Passo 2.5: Gerar Tráfego

Em outro terminal:

```bash
# Faça várias requisições
curl http://localhost:3001/tasks
curl http://localhost:3001/tasks
curl -X POST http://localhost:3001/tasks -H "Content-Type: application/json" -d '{"title":"Nova tarefa"}'
curl http://localhost:3001/tasks/sync
curl http://localhost:3001/tasks/export
curl http://localhost:3001/tasks/export
```

### Passo 2.6: Ver Traces no SigNoz

1. Abra: http://localhost:8080
2. Faça login (se necessário)
3. Vá em **"Traces"** no menu lateral
4. Você verá as requisições aparecendo! 🎉

**Clique em um trace para ver:**
- Duração total
- Spans individuais
- Atributos HTTP
- Status code
- Timestamp

---

## 🐍 Python

### Passo 2.1: Instalar Dependências

```bash
cd meu-projeto-python
source venv/bin/activate

pip install opentelemetry-api \
            opentelemetry-sdk \
            opentelemetry-exporter-otlp-proto-grpc \
            opentelemetry-instrumentation-flask \
            opentelemetry-instrumentation-requests
```

### Passo 2.2: Criar Arquivo de Instrumentação

Crie o arquivo `instrumentation.py` **NA MESMA PASTA que app.py**:

```python
# instrumentation.py
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION, DEPLOYMENT_ENVIRONMENT
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

print('🔧 Configurando OpenTelemetry...')

# PASSO 1: Definir recurso
resource = Resource.create({
    SERVICE_NAME: "meu-todo-app-python",
    SERVICE_VERSION: "1.0.0",
    DEPLOYMENT_ENVIRONMENT: "development",
})

# PASSO 2: Criar provider de traces
tracer_provider = TracerProvider(resource=resource)

# PASSO 3: Configurar exportador
otlp_exporter = OTLPSpanExporter(
    endpoint="http://localhost:4317",
    insecure=True,
)

# PASSO 4: Adicionar processador de spans
span_processor = BatchSpanProcessor(otlp_exporter)
tracer_provider.add_span_processor(span_processor)

# PASSO 5: Ativar provider
trace.set_tracer_provider(tracer_provider)

# PASSO 6: Auto-instrumentar Flask
FlaskInstrumentor().instrument()
RequestsInstrumentor().instrument()

print('⚡ OpenTelemetry iniciado!')
print('📊 Enviando traces para: http://localhost:4317')
print('🔍 Veja os dados em: http://localhost:8080\n')
```

### Passo 2.3: Modificar app.py

**IMPORTANTE:** Adicione esta linha NO INÍCIO do arquivo `app.py`:

```python
# app.py
import instrumentation  # ← PRIMEIRA LINHA! Antes do Flask!

from flask import Flask, request, jsonify
# ... resto do código continua igual
```

### Passo 2.4: Executar com Instrumentação

```bash
python app.py
```

### Passo 2.5: Gerar Tráfego

```bash
curl http://localhost:5001/tasks
curl -X POST http://localhost:5001/tasks -H "Content-Type: application/json" -d '{"title":"Nova tarefa"}'
curl http://localhost:5001/tasks/sync
curl http://localhost:5001/tasks/export
```

### Passo 2.6: Ver Traces no SigNoz

1. Abra: http://localhost:8080
2. Vá em "Traces"
3. Veja seus traces! 🎉

---

## 🔍 O Que Observar no SigNoz

### Na Lista de Traces

- **Service Name:** `meu-todo-app` (ou `meu-todo-app-python`)
- **Operations:** `GET /tasks`, `POST /tasks`, etc
- **Duration:** Tempo de cada requisição
- **Status:** Success ou Error

### Ao Clicar em um Trace

Você verá spans como:

```
GET /tasks                           [200] 145ms
├─ express.middleware                 5ms
└─ express.request_handler           140ms
```

### Nos Atributos

- `http.method`: GET, POST, PUT
- `http.route`: /tasks
- `http.status_code`: 200, 201, 404, 500
- `service.name`: meu-todo-app

---

## ✅ Checklist

- [ ] Dependências OpenTelemetry instaladas
- [ ] Arquivo `instrumentation.js/py` criado
- [ ] Aplicação executando com instrumentação
- [ ] Tráfego gerado
- [ ] Traces visíveis no SigNoz
- [ ] Consegue ver detalhes de cada trace

---

## 🎯 O Que Você Aprendeu

✅ Como instalar dependências do OpenTelemetry  
✅ Como criar configuração de instrumentação  
✅ Como carregar instrumentação ANTES da aplicação  
✅ Como auto-instrumentação funciona  
✅ Como ver traces no SigNoz  
✅ Como interpretar spans e atributos  

---

## 🤔 Exercícios

1. **Teste diferentes endpoints** e veja como os traces aparecem
2. **Gere um erro** (chame `/tasks/export` várias vezes)
3. **Veja operação lenta** (chame `/tasks/sync`)
4. **Compare traces** de endpoints rápidos vs lentos

---

## 🚀 Próximo Passo

Agora você tem instrumentação automática funcionando!

Mas e se você quiser rastrear operações específicas do SEU negócio?

**Continue em:** `../parte-3-spans-customizados/README.md`

Lá você vai aprender a criar seus próprios spans! 🎉


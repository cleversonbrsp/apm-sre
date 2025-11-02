# 🟢 Aplicação Node.js de Exemplo - SigNoz

Aplicação Node.js + Express totalmente instrumentada com OpenTelemetry para demonstrar observabilidade com SigNoz.

## 📋 Requisitos

- Node.js 14+ 
- npm ou yarn
- SigNoz rodando (veja /signoz/deploy/docker)
- OpenTelemetry Collector rodando

## 🚀 Instalação e Execução

### 1. Instalar Dependências

```bash
npm install
```

**Dependências principais:**
- `express`: Framework web
- `@opentelemetry/sdk-node`: SDK Node.js
- `@opentelemetry/auto-instrumentations-node`: Auto-instrumentação
- `@opentelemetry/exporter-otlp-grpc`: Exportar dados para SigNoz

### 2. Executar a Aplicação

```bash
npm start
```

A aplicação estará disponível em: **http://localhost:3000**

**Importante:** O arquivo `instrumentation.js` é carregado automaticamente via `-r`, então toda a instrumentação já está ativa!

### 3. Gerar Dados de Telemetria

Execute alguns requests para gerar dados:

```bash
# Health check
curl http://localhost:3000/api/health

# Listar usuários
curl http://localhost:3000/api/users

# Buscar usuário específico
curl http://localhost:3000/api/users/1

# Criar novo usuário
curl -X POST http://localhost:3000/api/users \
  -H "Content-Type: application/json" \
  -d '{"name":"João Silva","email":"joao@example.com","role":"admin"}'

# Endpoint que simula erro (20% das vezes)
curl http://localhost:3000/api/products

# Endpoint lento (1-3 segundos)
curl http://localhost:3000/api/slow
```

### 4. Ver Dados no SigNoz

Acesse: **http://localhost:8080**

Explore:
- **Traces**: Veja o rastreamento completo das requisições
- **Service Map**: Visualize as dependências
- **Métricas**: Performance, latency, erros

## 📁 Estrutura de Arquivos

```
app-nodejs/
├── package.json          # Dependências e scripts
├── instrumentation.js    # ⚡ Configuração OpenTelemetry
├── server.js             # Aplicação Express
└── README.md             # Este arquivo
```

## 🔍 Como Funciona a Instrumentação

### Auto-Instrumentação

Quando você executa `npm start`, o script usa:
```json
"start": "node -r ./instrumentation.js server.js"
```

O `-r` carrega o `instrumentation.js` **antes** de iniciar a aplicação. Isso significa:

✅ **Todas as requisições HTTP** são rastreadas automaticamente
✅ **Chamadas de banco de dados** são instrumentadas (quando configuradas)
✅ **Métricas de performance** são coletadas
✅ **Contexto é propagado** entre operações

### Configuração no instrumentation.js

```javascript
const sdk = new NodeSDK({
  resource: new Resource({
    [SemanticResourceAttributes.SERVICE_NAME]: 'signoz-example-nodejs',
    [SemanticResourceAttributes.SERVICE_VERSION]: '1.0.0',
  }),
  
  traceExporter: new OTLPTraceExporter({
    url: 'http://localhost:4317', // Otel Collector
  }),
  
  instrumentations: [getNodeAutoInstrumentations()],
});
```

## 🎯 Endpoints Disponíveis

| Método | Endpoint | Descrição | Observabilidade |
|--------|----------|-----------|-----------------|
| GET | `/api/health` | Health check | Status da aplicação |
| GET | `/api/users` | Lista usuários | Traces normais |
| GET | `/api/users/:id` | Busca usuário | Spans com atributos |
| POST | `/api/users` | Cria usuário | Operações de escrita |
| GET | `/api/products` | Lista produtos | Erros simulados (20%) |
| GET | `/api/slow` | Operação lenta | Métricas de latência |
| GET | `/api/redirect-demo` | Redirect | Múltiplos spans |

## 📊 Tipos de Dados Gerados

### 1. Traces

Cada requisição HTTP gera um trace completo:
```
Trace: GET /api/users
  ├─ Span: express:middleware
  ├─ Span: express:request_handler
  └─ Span: setTimeout (delay de DB)
```

### 2. Métricas

Automaticamente coletadas:
- **Latência**: Tempo de resposta por endpoint
- **Throughput**: Requisições por segundo
- **Erros**: Taxa de erro por endpoint
- **Status**: Distribuição de status HTTP

### 3. Atributos

Cada span inclui:
- `http.method`: GET, POST, etc
- `http.route`: /api/users
- `http.status_code`: 200, 404, 500
- `service.name`: signoz-example-nodejs
- `service.version`: 1.0.0

## 🔧 Configurações Avançadas

### Mudar Endpoint do Collector

No `instrumentation.js`, altere:
```javascript
traceExporter: new OTLPTraceExporter({
  url: 'http://SEU_COLLECTOR:4317',
}),
```

### Adicionar Atributos Customizados

No `server.js`, você pode adicionar atributos ao contexto:

```javascript
const { trace } = require('@opentelemetry/api');

const span = trace.getActiveSpan();
span.setAttribute('user.id', userId);
span.setAttribute('operation.type', 'create_user');
```

### Desabilitar Instrumentações Específicas

No `instrumentation.js`:
```javascript
instrumentations: [
  getNodeAutoInstrumentations({
    '@opentelemetry/instrumentation-fs': {
      enabled: false,
    },
  }),
],
```

## 🐛 Troubleshooting

### Não vejo dados no SigNoz

1. Verifique se o Otel Collector está rodando:
   ```bash
   docker ps | grep otel-collector
   ```

2. Verifique os logs:
   ```bash
   docker logs signoz-otel-collector
   ```

3. Teste a conexão:
   ```bash
   curl http://localhost:4317
   ```

### Erro ao instalar dependências

```bash
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

## 📚 Próximos Passos

1. ✅ Execute a aplicação e veja os dados no SigNoz
2. 🔍 Explore diferentes endpoints para gerar traces variados
3. 📊 Configure dashboards no SigNoz
4. 🔔 Configure alertas para erros e latência
5. 🔧 Adapte a instrumentação para suas aplicações

## 🔗 Links Úteis

- [OpenTelemetry Node.js](https://opentelemetry.io/docs/instrumentation/js/getting-started/nodejs/)
- [SigNoz Docs](https://signoz.io/docs/)
- [Express Auto-instrumentation](https://opentelemetry.io/docs/instrumentation/js/libraries/)
- [OTLP Exporter](https://opentelemetry.io/docs/specs/otlp/)


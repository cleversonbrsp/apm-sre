# 🐍 Aplicação Python de Exemplo - SigNoz

Aplicação Python + Flask totalmente instrumentada com OpenTelemetry para demonstrar observabilidade com SigNoz.

## 📋 Requisitos

- Python 3.8+
- pip
- SigNoz rodando (veja /signoz/deploy/docker)
- OpenTelemetry Collector rodando

## 🚀 Instalação e Execução

### 1. Criar Ambiente Virtual (Recomendado)

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

### 2. Instalar Dependências

```bash
pip install -r requirements.txt
```

**Dependências principais:**
- `flask`: Framework web
- `opentelemetry-api`: API OpenTelemetry
- `opentelemetry-sdk`: SDK Python
- `opentelemetry-exporter-otlp-proto-grpc`: Exportar dados para SigNoz
- `opentelemetry-instrumentation-flask`: Auto-instrumentação Flask
- `opentelemetry-instrumentation-requests`: Auto-instrumentação HTTP

### 3. Executar a Aplicação

```bash
python app.py
```

A aplicação estará disponível em: **http://localhost:5000**

**Importante:** O arquivo `instrumentation.py` é importado automaticamente no início do `app.py`, então toda a instrumentação já está ativa!

### 4. Gerar Dados de Telemetria

Execute alguns requests para gerar dados:

```bash
# Health check
curl http://localhost:5000/api/health

# Listar usuários
curl http://localhost:5000/api/users

# Buscar usuário específico
curl http://localhost:5000/api/users/1

# Criar novo usuário
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -d '{"name":"João Silva","email":"joao@example.com","role":"admin"}'

# Endpoint que simula erro (20% das vezes)
curl http://localhost:5000/api/products

# Endpoint com erro aleatório
curl http://localhost:5000/api/random-error

# Endpoint lento (1-3 segundos)
curl http://localhost:5000/api/slow
```

### 5. Ver Dados no SigNoz

Acesse: **http://localhost:8080**

Explore:
- **Traces**: Veja o rastreamento completo das requisições
- **Service Map**: Visualize as dependências
- **Métricas**: Performance, latency, erros

## 📁 Estrutura de Arquivos

```
app-python/
├── requirements.txt      # Dependências Python
├── instrumentation.py    # ⚡ Configuração OpenTelemetry
├── app.py                # Aplicação Flask
└── README.md             # Este arquivo
```

## 🔍 Como Funciona a Instrumentação

### Auto-Instrumentação

Quando você executa `python app.py`, a linha:
```python
import instrumentation  # noqa: F401
```

Carrega o módulo `instrumentation.py` **antes** de iniciar a aplicação Flask. Isso garante que:

✅ **Todas as requisições HTTP** são rastreadas automaticamente
✅ **Chamadas HTTP externas** são instrumentadas
✅ **Métricas de performance** são coletadas
✅ **Contexto é propagado** entre operações

### Configuração no instrumentation.py

```python
def setup_instrumentation():
    # Recurso: Identifica sua aplicação
    resource = Resource.create({
        SERVICE_NAME: "signoz-example-python",
        SERVICE_VERSION: "1.0.0",
        DEPLOYMENT_ENVIRONMENT: "development",
    })
    
    # Configura Provider de Traces
    tracer_provider = TracerProvider(resource=resource)
    
    # Exporta traces para SigNoz
    otlp_trace_exporter = OTLPSpanExporter(
        endpoint="http://localhost:4317",  # Otel Collector
        insecure=True,
    )
    
    # Habilita auto-instrumentação
    FlaskInstrumentor().instrument()
    RequestsInstrumentor().instrument()
```

## 🎯 Endpoints Disponíveis

| Método | Endpoint | Descrição | Observabilidade |
|--------|----------|-----------|-----------------|
| GET | `/api/health` | Health check | Status da aplicação |
| GET | `/api/users` | Lista usuários | Traces normais |
| GET | `/api/users/<id>` | Busca usuário | Spans com atributos |
| POST | `/api/users` | Cria usuário | Operações de escrita |
| GET | `/api/products` | Lista produtos | Erros simulados (20%) |
| GET | `/api/random-error` | Erro aleatório | Diferentes tipos de erro |
| GET | `/api/slow` | Operação lenta | Métricas de latência |

## 📊 Tipos de Dados Gerados

### 1. Traces

Cada requisição HTTP gera um trace completo:
```
Trace: GET /api/users
  ├─ Span: flask.request
  └─ Span: time.sleep (delay de DB)
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
- `service.name`: signoz-example-python
- `service.version`: 1.0.0

## 🔧 Configurações Avançadas

### Mudar Endpoint do Collector

No `instrumentation.py`, altere:
```python
otlp_trace_exporter = OTLPSpanExporter(
    endpoint="http://SEU_COLLECTOR:4317",
    insecure=True,
)
```

### Adicionar Atributos Customizados

No `app.py`, você pode adicionar atributos ao contexto:

```python
from opentelemetry import trace

# Obter tracer
tracer = trace.get_tracer(__name__)

# Adicionar atributos ao span atual
span = trace.get_current_span()
span.set_attribute("user.id", user_id)
span.set_attribute("operation.type", "create_user")
```

### Criar Spans Customizados

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

@app.route('/api/custom')
def custom_route():
    with tracer.start_as_current_span("custom_operation") as span:
        span.set_attribute("custom.attribute", "value")
        
        # Sua lógica aqui
        result = do_something()
        
        span.set_attribute("result.count", len(result))
        
        return jsonify(result)
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

### Erro ao importar módulos

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Erro "ModuleNotFoundError: No module named 'instrumentation'"

Certifique-se de que está executando `python app.py` no diretório correto:
```bash
cd app-python
python app.py
```

### Logs não aparecem

O Flask usa debug mode por padrão neste exemplo. Verifique:
- Console do terminal onde executou `python app.py`
- Logs do Otel Collector: `docker logs signoz-otel-collector`
- SigNoz UI em http://localhost:8080

## 📚 Próximos Passos

1. ✅ Execute a aplicação e veja os dados no SigNoz
2. 🔍 Explore diferentes endpoints para gerar traces variados
3. 📊 Configure dashboards no SigNoz
4. 🔔 Configure alertas para erros e latência
5. 🔧 Adapte a instrumentação para suas aplicações

## 🔗 Links Úteis

- [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/)
- [SigNoz Docs](https://signoz.io/docs/)
- [Flask Instrumentation](https://opentelemetry.io/docs/instrumentation/python/libraries/)
- [OTLP Exporter](https://opentelemetry.io/docs/specs/otlp/)

## 📝 Notas Importantes

### Ordem de Importação

**CRÍTICO:** O `instrumentation.py` DEVE ser importado antes do Flask:

```python
import instrumentation  # ← ANTES do Flask!
from flask import Flask  # ← DEPOIS da instrumentação
```

Isso garante que a auto-instrumentação capture todas as requisições.

### Ambiente Virtual

Sempre use um ambiente virtual para evitar conflitos de dependências:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Debug Mode

Este exemplo usa `debug=True` para desenvolvimento. Em produção:
```python
app.run(host='0.0.0.0', port=5000, debug=False)
```


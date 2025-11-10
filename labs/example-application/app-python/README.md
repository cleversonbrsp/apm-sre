#  Python Sample Application - SigNoz

Python + Flask application fully instrumented with OpenTelemetry to showcase observability with SigNoz.

##  Requirements

- Python 3.8+
- pip
- SigNoz running (see `/signoz/deploy/docker`)
- OpenTelemetry Collector running

##  Setup and Execution

### 1. Create a Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**Key dependencies:**
- `flask`: Web framework
- `opentelemetry-api`: OpenTelemetry API
- `opentelemetry-sdk`: Python SDK
- `opentelemetry-exporter-otlp-proto-grpc`: Exports data to SigNoz
- `opentelemetry-instrumentation-flask`: Flask auto instrumentation
- `opentelemetry-instrumentation-requests`: HTTP auto instrumentation

### 3. Run the Application

```bash
python app.py
```

The application will be available at **http://localhost:5000**

**Important:** The `instrumentation.py` module is automatically imported at the top of `app.py`, so every instrumentation hook is already active!

### 4. Generate Telemetry Data

Trigger a few requests to generate data:

```bash
# Health check
curl http://localhost:5000/api/health

# List users
curl http://localhost:5000/api/users

# Fetch a specific user
curl http://localhost:5000/api/users/1

# Create a new user
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -d '{"name":"John Smith","email":"john@example.com","role":"admin"}'

# Endpoint that simulates errors (20% of the time)
curl http://localhost:5000/api/products

# Endpoint with random errors
curl http://localhost:5000/api/random-error

# Slow endpoint (1-3 seconds)
curl http://localhost:5000/api/slow
```

### 5. View Data in SigNoz

Open **http://localhost:8080**

Explore:
- **Traces** – Inspect the full lifecycle of requests
- **Service Map** – Visualize dependencies
- **Metrics** – Performance, latency, errors

##  File Structure

```
app-python/
├── requirements.txt      # Python dependencies
├── instrumentation.py    #  OpenTelemetry configuration
├── app.py                # Flask application
└── README.md             # This file
```

##  How the Instrumentation Works

### Auto Instrumentation

When you run `python app.py`, the line:
```python
import instrumentation  # noqa: F401
```

loads the `instrumentation.py` module **before** the Flask app starts. That ensures:

 **All HTTP requests** are automatically traced  
 **Outgoing HTTP calls** are instrumented  
 **Performance metrics** are collected  
 **Context is propagated** across operations  

### Configuration in instrumentation.py

```python
def setup_instrumentation():
    # Resource: identifies your application
    resource = Resource.create({
        SERVICE_NAME: "signoz-example-python",
        SERVICE_VERSION: "1.0.0",
        DEPLOYMENT_ENVIRONMENT: "development",
    })

    # Configure the tracer provider
    tracer_provider = TracerProvider(resource=resource)

    # Export traces to SigNoz
    otlp_trace_exporter = OTLPSpanExporter(
        endpoint="http://localhost:4317",  # OTel Collector
        insecure=True,
    )

    # Enable auto instrumentation
    FlaskInstrumentor().instrument()
    RequestsInstrumentor().instrument()
```

##  Available Endpoints

| Method | Endpoint | Description | Observability Notes |
|--------|----------|-------------|---------------------|
| GET | `/api/health` | Health check | Application status |
| GET | `/api/users` | List users | Standard traces |
| GET | `/api/users/<id>` | Fetch a user | Spans with attributes |
| POST | `/api/users` | Create user | Write operations |
| GET | `/api/products` | List products | Simulated errors (20%) |
| GET | `/api/random-error` | Random error | Different failure types |
| GET | `/api/slow` | Slow operation | Latency metrics |

##  Telemetry Types Generated

### 1. Traces

Each HTTP request yields a full trace:
```
Trace: GET /api/users
  ├─ Span: flask.request
  └─ Span: time.sleep (DB delay simulation)
```

### 2. Metrics

Collected automatically:
- **Latency**: Response time per endpoint
- **Throughput**: Requests per second
- **Errors**: Error rate per endpoint
- **Status**: HTTP status distribution

### 3. Attributes

Every span includes:
- `http.method`: GET, POST, etc.
- `http.route`: /api/users
- `http.status_code`: 200, 404, 500
- `service.name`: signoz-example-python
- `service.version`: 1.0.0

##  Advanced Configuration

### Change Collector Endpoint

In `instrumentation.py`, update:
```python
otlp_trace_exporter = OTLPSpanExporter(
    endpoint="http://YOUR_COLLECTOR:4317",
    insecure=True,
)
```

### Add Custom Attributes

In `app.py`, enrich the active span:

```python
from opentelemetry import trace

# Obtain tracer
tracer = trace.get_tracer(__name__)

# Attach attributes to the current span
span = trace.get_current_span()
span.set_attribute("user.id", user_id)
span.set_attribute("operation.type", "create_user")
```

### Create Custom Spans

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

@app.route('/api/custom')
def custom_route():
    with tracer.start_as_current_span("custom_operation") as span:
        span.set_attribute("custom.attribute", "value")

        # Your logic here
        result = do_something()

        span.set_attribute("result.count", len(result))

        return jsonify(result)
```

##  Troubleshooting

### Not seeing data in SigNoz

1. Confirm the OTel Collector is running:
   ```bash
   docker ps | grep otel-collector
   ```

2. Check the logs:
   ```bash
   docker logs signoz-otel-collector
   ```

3. Test connectivity:
   ```bash
   curl http://localhost:4317
   ```

### Module import errors

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Error "ModuleNotFoundError: No module named 'instrumentation'"

Make sure you are running `python app.py` from the correct directory:
```bash
cd app-python
python app.py
```

### Logs do not appear

Flask uses debug mode by default in this example. Check:
- The terminal where you ran `python app.py`
- OTel Collector logs: `docker logs signoz-otel-collector`
- SigNoz UI at http://localhost:8080

##  Next Steps

1.  Run the application and confirm data in SigNoz  
2.  Exercise different endpoints to generate varied traces  
3.  Build dashboards in SigNoz  
4.  Configure alerts for errors and latency  
5.  Adapt the instrumentation to your own services  

##  Helpful Links

- [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/)
- [SigNoz Docs](https://signoz.io/docs/)
- [Flask Instrumentation](https://opentelemetry.io/docs/instrumentation/python/libraries/)
- [OTLP Exporter](https://opentelemetry.io/docs/specs/otlp/)

##  Important Notes

### Import Order

**CRITICAL:** `instrumentation.py` MUST be imported before Flask:

```python
import instrumentation  # ← BEFORE Flask!
from flask import Flask  # ← AFTER instrumentation
```

This guarantees that auto instrumentation captures every request.

### Virtual Environment

Always use a virtual environment to avoid dependency conflicts:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Debug Mode

This sample uses `debug=True` for development. In production:
```python
app.run(host='0.0.0.0', port=5000, debug=False)
```


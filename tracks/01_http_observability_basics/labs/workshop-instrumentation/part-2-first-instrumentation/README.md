#  Part 2: Adding Instrumentation

**Goal:** Wire OpenTelemetry into the application you created!

---

##  What You’ll Do

1. Install OpenTelemetry dependencies  
2. Create an instrumentation file  
3. Configure the exporter  
4. Load instrumentation before the app starts  
5. View traces in SigNoz! 

---

##  Node.js

### Step 2.1: Install Dependencies

```bash
cd my-nodejs-project

npm install @opentelemetry/api \
            @opentelemetry/sdk-node \
            @opentelemetry/auto-instrumentations-node \
            @opentelemetry/exporter-trace-otlp-grpc \
            @opentelemetry/resources \
            @opentelemetry/semantic-conventions
```

**Give it a minute or two – it can take a little while.**

### Step 2.2: Create the Instrumentation File

Create `instrumentation.js` **in the SAME folder as app.js**:

```javascript
// instrumentation.js
const { NodeSDK } = require('@opentelemetry/sdk-node');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-grpc');
const { Resource } = require('@opentelemetry/resources');
const { SemanticResourceAttributes } = require('@opentelemetry/semantic-conventions');

console.log(' Setting up OpenTelemetry…');

// STEP 1: Define resource metadata for your service
const resource = new Resource({
  [SemanticResourceAttributes.SERVICE_NAME]: 'my-todo-app',
  [SemanticResourceAttributes.SERVICE_VERSION]: '1.0.0',
  [SemanticResourceAttributes.DEPLOYMENT_ENVIRONMENT]: 'development',
});

// STEP 2: Configure the trace exporter
const traceExporter = new OTLPTraceExporter({
  url: 'http://localhost:4317', // OTel Collector
});

// STEP 3: Create and configure the SDK
const sdk = new NodeSDK({
  resource,
  traceExporter,
  instrumentations: [
    getNodeAutoInstrumentations({
      // Disable filesystem instrumentation (not useful here)
      '@opentelemetry/instrumentation-fs': {
        enabled: false,
      },
    }),
  ],
});

// STEP 4: Start collecting telemetry
sdk.start();
console.log(' OpenTelemetry started!');
console.log(' Sending traces to: http://localhost:4317');
console.log(' View telemetry at: http://localhost:8080\n');

// STEP 5: Graceful shutdown
process.on('SIGTERM', () => {
  sdk.shutdown()
    .then(() => console.log(' Telemetry stopped'))
    .finally(() => process.exit(0));
});
```

### Step 2.3: Update package.json

Edit `package.json` and add:

```json
{
  "scripts": {
    "start": "node -r ./instrumentation.js app.js"
  }
}
```

**IMPORTANT:** The `-r` flag loads `instrumentation.js` BEFORE `app.js`.

### Step 2.4: Run with Instrumentation

```bash
npm start
```

You should see:

```
 Setting up OpenTelemetry…
 OpenTelemetry started!
 Sending traces to: http://localhost:4317
 View telemetry at: http://localhost:8080

 Server running at http://localhost:3001
```

### Step 2.5: Generate Traffic

From a second terminal:

```bash
# Fire a few requests
curl http://localhost:3001/tasks
curl http://localhost:3001/tasks
curl -X POST http://localhost:3001/tasks -H "Content-Type: application/json" -d '{"title":"New task"}'
curl http://localhost:3001/tasks/sync
curl http://localhost:3001/tasks/export
curl http://localhost:3001/tasks/export
```

### Step 2.6: View Traces in SigNoz

1. Open http://localhost:8080  
2. Sign in if required  
3. Click **“Traces”** in the sidebar  
4. You should see the requests you just generated! 

**Open a trace to explore:**
- Total duration  
- Individual spans  
- HTTP attributes  
- Status code  
- Timestamp  

---

##  Python

### Step 2.1: Install Dependencies

```bash
cd my-python-project
source venv/bin/activate

pip install opentelemetry-api \
            opentelemetry-sdk \
            opentelemetry-exporter-otlp-proto-grpc \
            opentelemetry-instrumentation-flask \
            opentelemetry-instrumentation-requests
```

### Step 2.2: Create the Instrumentation File

Create `instrumentation.py` **in the SAME folder as app.py**:

```python
# instrumentation.py
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION, DEPLOYMENT_ENVIRONMENT
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

print(' Setting up OpenTelemetry…')

# STEP 1: Define the resource
resource = Resource.create({
    SERVICE_NAME: "my-todo-app-python",
    SERVICE_VERSION: "1.0.0",
    DEPLOYMENT_ENVIRONMENT: "development",
})

# STEP 2: Create the tracer provider
tracer_provider = TracerProvider(resource=resource)

# STEP 3: Configure the exporter
otlp_exporter = OTLPSpanExporter(
    endpoint="http://localhost:4317",
    insecure=True,
)

# STEP 4: Add the span processor
span_processor = BatchSpanProcessor(otlp_exporter)
tracer_provider.add_span_processor(span_processor)

# STEP 5: Activate the provider
trace.set_tracer_provider(tracer_provider)

# STEP 6: Auto-instrument Flask and requests
FlaskInstrumentor().instrument()
RequestsInstrumentor().instrument()

print(' OpenTelemetry started!')
print(' Sending traces to: http://localhost:4317')
print(' View telemetry at: http://localhost:8080\n')
```

### Step 2.3: Update app.py

**IMPORTANT:** Add this as the VERY FIRST line in `app.py`:

```python
# app.py
import instrumentation  # ← must run before Flask is imported!

from flask import Flask, request, jsonify
# ... keep the rest of the file exactly the same
```

### Step 2.4: Run with Instrumentation

```bash
python app.py
```

### Step 2.5: Generate Traffic

```bash
curl http://localhost:5001/tasks
curl -X POST http://localhost:5001/tasks -H "Content-Type: application/json" -d '{"title":"New task"}'
curl http://localhost:5001/tasks/sync
curl http://localhost:5001/tasks/export
```

### Step 2.6: View Traces in SigNoz

1. Open http://localhost:8080  
2. Navigate to “Traces”  
3. Inspect your new telemetry! 

---

##  What to Look For in SigNoz

### Trace List

- **Service Name:** `my-todo-app` (or `my-todo-app-python`)  
- **Operations:** `GET /tasks`, `POST /tasks`, etc.  
- **Duration:** Time spent per request  
- **Status:** Success or Error  

### When Opening a Trace

You should see spans like:

```
GET /tasks                           [200] 145ms
├─ express.middleware                 5ms
└─ express.request_handler          140ms
```

### Span Attributes

- `http.method`: GET, POST, PUT  
- `http.route`: /tasks  
- `http.status_code`: 200, 201, 404, 500  
- `service.name`: my-todo-app  

---

##  Checklist

- [ ] OpenTelemetry dependencies installed  
- [ ] `instrumentation.js/py` created  
- [ ] App running with instrumentation enabled  
- [ ] Traffic generated  
- [ ] Traces visible in SigNoz  
- [ ] Able to inspect trace details  

---

##  What You Learned

 How to install OpenTelemetry dependencies  
 How to configure instrumentation  
 How to load instrumentation BEFORE the app boots  
 How auto-instrumentation works  
 How to view traces in SigNoz  
 How to interpret spans and attributes  

---

##  Practice Ideas

1. **Hit different endpoints** and observe the traces  
2. **Trigger an error** by calling `/tasks/export` repeatedly  
3. **Trigger the slow path** by calling `/tasks/sync`  
4. **Compare traces** for fast vs. slow endpoints  

---

##  Next Step

Auto-instrumentation is live!  
What if you need visibility into custom business logic?

**Continue with:** `../part-3-custom-spans/README.md`

That’s where you’ll create your own spans! 


#  Detailed Guide: How to Instrument Applications

This guide explains, **step by step**, how to instrument your applications so they can send telemetry to SigNoz.

---

##  Table of Contents

1. [What Is Instrumentation?](#what-is-instrumentation)
2. [Observability Architecture](#observability-architecture)
3. [Step by Step: Node.js](#step-by-step-nodejs)
4. [Step by Step: Python](#step-by-step-python)
5. [How It Works in Practice](#how-it-works-in-practice)
6. [Manual vs Automatic Instrumentation](#manual-vs-automatic-instrumentation)
7. [Adapting It to Your App](#adapting-it-to-your-app)

---

## What Is Instrumentation?

**Instrumentation** is the process of adding code to your application so that it can collect telemetry data (traces, metrics, and logs).

###  Simple Analogy

Picture your application as a car:

- **Without instrumentation**: A car without a dashboard. You drive, but you have no idea about speed, temperature, or fuel.
- **With instrumentation**: A car with a complete dashboard. You see everything happening in real time.

###  Types of Data Collected

1. **TRACES**   
   - What: The journey of a request from start to finish  
   - When to use: “Why is this request slow?”  
   - Example: HTTP request → DB query → External API call → Response

2. **METRICS**   
   - What: Numeric values over time  
   - When to use: “How many requests per second?”  
   - Example: Average latency, error rate, memory usage

3. **LOGS**   
   - What: Events that happen inside your app  
   - When to use: “What happened right before the error?”  
   - Example: “User created”, “Failed to connect to DB”

---

## Observability Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│ YOUR APPLICATION                                                 │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐     │
│  │ 1. Your Code (Express, Flask, etc.)                    │     │
│  └────────────┬───────────────────────────────────────────┘     │
│               │                                                  │
│  ┌────────────▼───────────────────────────────────────────┐     │
│  │ 2. OpenTelemetry SDK                                   │     │
│  │    - Auto instruments libraries (HTTP, DB, etc.)       │     │
│  │    - Collects traces, metrics, logs                    │     │
│  │    - Adds context (IDs, attributes)                    │     │
│  └────────────┬───────────────────────────────────────────┘     │
└───────────────┼──────────────────────────────────────────────────┘
                │
                │ 3. Sends data via OTLP (OpenTelemetry Protocol)
                ▼
┌──────────────────────────────────────────────────────────────────┐
│ OTEL COLLECTOR (port 4317)                                       │
│  - Receives data from multiple applications                      │
│  - Processes and filters                                          │
│  - Forwards to backends                                           │
└────────────┬─────────────────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────────────────┐
│ CLICKHOUSE (Database)                                            │
│  - Stores traces, metrics, logs                                  │
└────────────┬─────────────────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────────────────┐
│ SIGNOZ UI (port 8080)                                            │
│  - Visualizes telemetry                                          │
│  - Dashboards, alerts, analytics                                 │
└──────────────────────────────────────────────────────────────────┘
```

---

## Step by Step: Node.js

###  Project Structure

```
your-project/
├── package.json          ← 1. Add dependencies here
├── instrumentation.js    ← 2. CREATE this configuration file
├── server.js             ← 3. Your existing code
└── node_modules/         ← 4. Created by npm install
```

###  STEP 1: Add Dependencies

**WHERE:** `package.json`

**WHAT:** Add the OpenTelemetry packages

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

**RUN:**
```bash
npm install
```

**WHAT EACH PACKAGE DOES:**

| Package | Purpose |
|---------|---------|
| `@opentelemetry/api` | Core OpenTelemetry API |
| `@opentelemetry/sdk-node` | Node.js SDK (main engine) |
| `@opentelemetry/auto-instrumentations-node` |  Auto instruments Express, HTTP, etc. |
| `@opentelemetry/exporter-trace-otlp-grpc` | Sends traces to SigNoz |
| `@opentelemetry/resources` | Sets application metadata |
| `@opentelemetry/semantic-conventions` | Naming standards |

---

###  STEP 2: Create the Instrumentation File

**WHERE:** Create `instrumentation.js` **at the project root**

**WHAT:** Configure the OpenTelemetry SDK

```javascript
// instrumentation.js
const { NodeSDK } = require('@opentelemetry/sdk-node');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-grpc');
const { Resource } = require('@opentelemetry/resources');
const { SemanticResourceAttributes } = require('@opentelemetry/semantic-conventions');

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// STEP 2.1: Define the Resource (identifies your app)
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
const resource = new Resource({
  [SemanticResourceAttributes.SERVICE_NAME]: 'my-application',  // ← UPDATE THIS
  [SemanticResourceAttributes.SERVICE_VERSION]: '1.0.0',
  [SemanticResourceAttributes.DEPLOYMENT_ENVIRONMENT]: 'production',
});

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// STEP 2.2: Configure the Trace Exporter
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
const traceExporter = new OTLPTraceExporter({
  url: 'http://localhost:4317',  // ← OTel Collector endpoint
  // If the collector is remote:
  // url: 'http://YOUR_SERVER:4317',
});

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// STEP 2.3: Configure the SDK
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
const sdk = new NodeSDK({
  resource,
  traceExporter,

  //  MAGIC HAPPENS HERE: Auto instrumentation
  instrumentations: [
    getNodeAutoInstrumentations({
      // Disable instrumentations you don't need
      '@opentelemetry/instrumentation-fs': {
        enabled: false,  // File system is rarely useful
      },
    }),
  ],
});

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// STEP 2.4: Start the SDK
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
sdk.start();
console.log(' OpenTelemetry initialized');

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// STEP 2.5: Graceful shutdown
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
process.on('SIGTERM', () => {
  sdk.shutdown()
    .then(() => console.log(' Telemetry stopped'))
    .finally(() => process.exit(0));
});
```

**LINE-BY-LINE EXPLANATION:**

```javascript
const resource = new Resource({...});
```
- **What:** Creates metadata about your application  
- **Why:** SigNoz uses it to identify which service produced the data  
- **Update:** Set `SERVICE_NAME` to your app name

```javascript
const traceExporter = new OTLPTraceExporter({...});
```
- **What:** Defines WHERE traces are sent  
- **Why:** Connects your app to the OTel Collector  
- **Update:** Change `url` if the collector is remote

```javascript
instrumentations: [getNodeAutoInstrumentations()]
```
- **What:** Enables automatic instrumentation  
- **Why:** Tracks HTTP, Express, DB without touching your code  
- **Update:** Disable libraries you don't use

```javascript
sdk.start();
```
- **What:** Starts capturing data  
- **Why:** From this point on, everything is traced!

---

###  STEP 3: Load Instrumentation BEFORE Your App

**WHERE:** `package.json` → scripts

**WHAT:** Use `-r` (require) so instrumentation loads first

```json
{
  "scripts": {
    "start": "node -r ./instrumentation.js server.js"
  }
}
```

**EXPLANATION:**

```
node -r ./instrumentation.js server.js
     ↑                        ↑
     |                        |
   Load first             Your app
```

**CRITICAL ORDER:**

1.  `instrumentation.js` is loaded FIRST  
2.  OpenTelemetry configures itself  
3.  Auto instrumentation turns on  
4.  `server.js` loads (already instrumented!)

** IF YOU LOAD IN THE WRONG ORDER:**
```javascript
//  WRONG – Won’t work!
const express = require('express');  // Express loaded first
require('./instrumentation');        // Too late!
```

** CORRECT ORDER:**
```bash
node -r ./instrumentation.js server.js
# Instrumentation loads BEFORE Express!
```

---

###  STEP 4: Your Code DOES NOT Change!

**WHERE:** `server.js` (your application)

**WHAT:** NOTHING! Keep coding as usual.

```javascript
// server.js – UNCHANGED!
const express = require('express');
const app = express();

app.get('/users', (req, res) => {
  // Your normal code
  res.json({ users: [] });
});

app.listen(3000);
```

** MAGIC:** Without touching your code, OpenTelemetry is already:
-  Tracking every HTTP request
-  Measuring latency
-  Capturing errors
-  Sending data to SigNoz

---

###  STEP 5: Run and Validate

**RUN:**
```bash
npm start
```

**YOU’LL SEE:**
```
 OpenTelemetry initialized
Server running on port 3000
```

**TEST:**
```bash
curl http://localhost:3000/users
```

**CHECK IN SIGNOZ:**
1. Visit http://localhost:8080  
2. Open “Traces”  
3. Look for the `GET /users` trace!

---

## Step by Step: Python

###  Project Structure

```
your-project/
├── requirements.txt      ← 1. Add dependencies here
├── instrumentation.py    ← 2. CREATE this file
├── app.py                ← 3. Your existing code
└── venv/                 ← 4. Created by pip install
```

###  STEP 1: Add Dependencies

**WHERE:** `requirements.txt`

**WHAT:**
```txt
Flask==3.0.0
opentelemetry-api==1.21.0
opentelemetry-sdk==1.21.0
opentelemetry-exporter-otlp-proto-grpc==1.21.0
opentelemetry-instrumentation-flask==0.42b0
opentelemetry-instrumentation-requests==0.42b0
```

**RUN:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

###  STEP 2: Create the Instrumentation File

**WHERE:** Create `instrumentation.py` **at the project root**

**WHAT:**

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
# STEP 2.1: Define the Resource
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
resource = Resource.create({
    SERVICE_NAME: "my-python-application",  # ← UPDATE THIS
    SERVICE_VERSION: "1.0.0",
})

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 2.2: Configure the Tracer Provider
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
tracer_provider = TracerProvider(resource=resource)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 2.3: Configure the Exporter
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
otlp_exporter = OTLPSpanExporter(
    endpoint="http://localhost:4317",  # ← Collector endpoint
    insecure=True,
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 2.4: Add the Span Processor
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
span_processor = BatchSpanProcessor(otlp_exporter)
tracer_provider.add_span_processor(span_processor)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 2.5: Activate the Provider
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
trace.set_tracer_provider(tracer_provider)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 2.6: Auto instrument Flask and Requests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FlaskInstrumentor().instrument()     #  Instruments Flask
RequestsInstrumentor().instrument()  #  Instruments HTTP requests

print(" OpenTelemetry initialized")
```

---

###  STEP 3: Import BEFORE Flask

**WHERE:** `app.py` (first line!)

**WHAT:**

```python
# app.py
import instrumentation  # ← FIRST LINE! BEFORE FLASK!

from flask import Flask  # ← Only now import Flask

app = Flask(__name__)

@app.route('/users')
def get_users():
    return {'users': []}

if __name__ == '__main__':
    app.run(port=5000)
```

**CRITICAL ORDER:**

```python
#  CORRECT
import instrumentation  # 1. Instrumentation FIRST
from flask import Flask # 2. Flask AFTER

#  WRONG
from flask import Flask  # Flask first
import instrumentation   # Too late!
```

---

###  STEP 4: Run and Validate

**RUN:**
```bash
python app.py
```

**TEST:**
```bash
curl http://localhost:5000/users
```

**CHECK IN SIGNOZ:**
- Visit http://localhost:8080  
- Inspect the traces!

---

## How It Works in Practice

###  Full Request Flow

```
1. Request arrives
   └─→ GET /users
       │
2. OpenTelemetry creates a TRACE
   └─→ Trace ID: abc123...
       │
3. OpenTelemetry creates an HTTP REQUEST SPAN
   └─→ Span: "GET /users"
       ├─ http.method: GET
       ├─ http.route: /users
       ├─ http.status_code: 200
       └─ duration: 45 ms
       │
4. Your code runs (auto instrumented)
   └─→ If DB is called, another SPAN is created
       └─→ Span: "SELECT * FROM users"
           └─ duration: 30 ms
       │
5. Response is sent
   └─→ Span is finished
       │
6. Data is sent to the OTel Collector
   └─→ OTLP gRPC → localhost:4317
       │
7. Collector processes and stores in ClickHouse
   └─→ Data persisted
       │
8. SigNoz UI displays the trace
   └─→ You inspect it on the dashboard!
```

###  What You See in SigNoz

**Full trace:**
```
GET /users                     [200] 45 ms
├─ express.middleware          5 ms
├─ express.request_handler     40 ms
│  └─ db.query                 30 ms
│     └─ SELECT * FROM users
└─ express.response            < 1 ms
```

---

## Manual vs Automatic Instrumentation

###  Automatic Instrumentation (Recommended)

**What:** OpenTelemetry instruments libraries automatically

**Benefits:**
-  No code changes required
-  Covers common cases (HTTP, DB, cache)
-  Fast to implement

**Supported libraries include:**
- HTTP/HTTPS
- Express, Koa, Fastify (Node.js)
- Flask, Django, FastAPI (Python)
- PostgreSQL, MySQL, MongoDB
- Redis, Memcached
- GraphQL
- gRPC

###  Manual Instrumentation

**When:** For business-specific operations

**Node.js example:**
```javascript
const { trace, SpanStatusCode } = require('@opentelemetry/api');

app.get('/process-payment', async (req, res) => {
  const tracer = trace.getTracer('my-app');

  // Create custom span
  const span = tracer.startSpan('process_payment');

  try {
    // Add custom attributes
    span.setAttribute('payment.amount', 100.00);
    span.setAttribute('payment.currency', 'USD');
    span.setAttribute('user.id', '123');

    // Your logic
    await processPayment();

    span.setStatus({ code: SpanStatusCode.OK });
  } catch (error) {
    span.setStatus({
      code: SpanStatusCode.ERROR,
      message: error.message,
    });
    throw error;
  } finally {
    span.end();  // ALWAYS end the span!
  }

  res.json({ status: 'ok' });
});
```

**Python example:**
```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

@app.route('/process-payment')
def process_payment():
    # Create custom span
    with tracer.start_as_current_span("process_payment") as span:
        # Add attributes
        span.set_attribute("payment.amount", 100.00)
        span.set_attribute("payment.currency", "USD")

        # Your logic
        result = process_payment_logic()

        return {'status': 'ok'}
```

---

## Adapting It to Your App

###  Instrumentation Checklist

1. **Identify your stack**
   - [ ] Language: Node.js, Python, Go, Java?
   - [ ] Framework: Express, Flask, Spring?
   - [ ] Database: PostgreSQL, MongoDB?
   - [ ] Cache: Redis, Memcached?

2. **Install dependencies**
   - [ ] OpenTelemetry SDK
   - [ ] Auto instrumentations for your stack
   - [ ] OTLP exporter

3. **Create the instrumentation file**
   - [ ] Configure the resource (`SERVICE_NAME`)
   - [ ] Configure the exporter (endpoint)
   - [ ] Enable auto instrumentations

4. **Load BEFORE your application**
   - [ ] Node.js: `-r ./instrumentation.js`
   - [ ] Python: `import instrumentation` (first line)

5. **Test**
   - [ ] Run the app
   - [ ] Send requests
   - [ ] Inspect traces in SigNoz

###  Where Should You Instrument?

**Priorities:**

1. **High priority (always instrument):**
   -  HTTP/API requests
   -  Database calls
   -  Cache operations
   -  External API calls

2. **Medium priority:**
   -  Queue processing (RabbitMQ, Kafka)
   -  File uploads/downloads
   -  Authentication flows

3. **Low priority (only if needed):**
   -  File system operations
   -  Internal calculations
   -  String manipulation

###  Real-Life Reusable Example

```javascript
// instrumentation.js (works for any Node.js app)
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

You can reuse this in ANY Node.js application! 

---

##  Summary

1. **Install** OpenTelemetry dependencies  
2. **Create** `instrumentation.js/py`  
3. **Configure** the resource and exporter  
4. **Load it BEFORE** your application  
5. **Done!** Your app is instrumented automatically

**The magic is:** You don’t need to modify your application code! 


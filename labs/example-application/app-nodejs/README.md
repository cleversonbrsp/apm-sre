# 🟢 Node.js Sample Application - SigNoz

Node.js + Express application fully instrumented with OpenTelemetry to demonstrate observability with SigNoz.

## 📋 Prerequisites

- Node.js 14+
- npm or yarn
- SigNoz running (see `/signoz/deploy/docker`)
- OpenTelemetry Collector running

## 🚀 Installation and Execution

### 1. Install Dependencies

```bash
npm install
```

**Key dependencies:**
- `express`: Web framework
- `@opentelemetry/sdk-node`: Node.js SDK
- `@opentelemetry/auto-instrumentations-node`: Auto instrumentation
- `@opentelemetry/exporter-otlp-grpc`: Exports data to SigNoz

### 2. Start the Application

```bash
npm start
```

The application will be available at **http://localhost:3000**

**Important:** The `instrumentation.js` file is automatically loaded via `-r`, so all instrumentation is enabled out of the box!

### 3. Generate Telemetry Data

Send a few requests to produce telemetry:

```bash
# Health check
curl http://localhost:3000/api/health

# List users
curl http://localhost:3000/api/users

# Fetch a specific user
curl http://localhost:3000/api/users/1

# Create a new user
curl -X POST http://localhost:3000/api/users \
  -H "Content-Type: application/json" \
  -d '{"name":"John Smith","email":"john@example.com","role":"admin"}'

# Endpoint that simulates errors (20% of the time)
curl http://localhost:3000/api/products

# Slow endpoint (1-3 seconds)
curl http://localhost:3000/api/slow
```

### 4. View Data in SigNoz

Open **http://localhost:8080**

Explore:
- **Traces**: Inspect the complete request lifecycle
- **Service Map**: Visualize dependencies
- **Metrics**: Performance, latency, errors

## 📁 File Structure

```
app-nodejs/
├── package.json          # Dependencies and scripts
├── instrumentation.js    # ⚡ OpenTelemetry configuration
├── server.js             # Express application
└── README.md             # This file
```

## 🔍 How the Instrumentation Works

### Auto-Instrumentation

When you run `npm start`, the script uses:
```json
"start": "node -r ./instrumentation.js server.js"
```

The `-r` flag loads `instrumentation.js` **before** the application starts. This ensures:

✅ **All HTTP requests** are automatically traced  
✅ **Database calls** are instrumented (when configured)  
✅ **Performance metrics** are collected  
✅ **Context propagation** across operations  

### Configuration in instrumentation.js

```javascript
const sdk = new NodeSDK({
  resource: new Resource({
    [SemanticResourceAttributes.SERVICE_NAME]: 'signoz-example-nodejs',
    [SemanticResourceAttributes.SERVICE_VERSION]: '1.0.0',
  }),

  traceExporter: new OTLPTraceExporter({
    url: 'http://localhost:4317', // OTel Collector
  }),

  instrumentations: [getNodeAutoInstrumentations()],
});
```

## 🎯 Available Endpoints

| Method | Endpoint | Description | Observability Notes |
|--------|----------|-------------|---------------------|
| GET | `/api/health` | Health check | Application status |
| GET | `/api/users` | List users | Standard traces |
| GET | `/api/users/:id` | Fetch a user | Spans with attributes |
| POST | `/api/users` | Create user | Write operations |
| GET | `/api/products` | List products | Simulated errors (20%) |
| GET | `/api/slow` | Slow operation | Latency metrics |
| GET | `/api/redirect-demo` | Redirect | Multiple spans |

## 📊 Telemetry Types Generated

### 1. Traces

Each HTTP request generates a complete trace:
```
Trace: GET /api/users
  ├─ Span: express:middleware
  ├─ Span: express:request_handler
  └─ Span: setTimeout (DB delay simulation)
```

### 2. Metrics

Collected automatically:
- **Latency**: Response time per endpoint
- **Throughput**: Requests per second
- **Errors**: Error rate per endpoint
- **Status**: HTTP status code distribution

### 3. Attributes

Each span includes:
- `http.method`: GET, POST, etc.
- `http.route`: /api/users
- `http.status_code`: 200, 404, 500
- `service.name`: signoz-example-nodejs
- `service.version`: 1.0.0

## 🔧 Advanced Configuration

### Change Collector Endpoint

In `instrumentation.js`, update:
```javascript
traceExporter: new OTLPTraceExporter({
  url: 'http://YOUR_COLLECTOR:4317',
}),
```

### Add Custom Attributes

In `server.js`, you can enrich the active span:

```javascript
const { trace } = require('@opentelemetry/api');

const span = trace.getActiveSpan();
span.setAttribute('user.id', userId);
span.setAttribute('operation.type', 'create_user');
```

### Disable Specific Instrumentations

In `instrumentation.js`:
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

### Not seeing data in SigNoz

1. Check if the OTel Collector is running:
   ```bash
   docker ps | grep otel-collector
   ```

2. Inspect the logs:
   ```bash
   docker logs signoz-otel-collector
   ```

3. Test connectivity:
   ```bash
   curl http://localhost:4317
   ```

### Dependency installation errors

```bash
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

## 📚 Next Steps

1. ✅ Run the application and confirm data in SigNoz  
2. 🔍 Exercise different endpoints to generate varied traces  
3. 📊 Build dashboards in SigNoz  
4. 🔔 Configure alerts for errors and latency  
5. 🔧 Adapt the instrumentation to your own services  

## 🔗 Helpful Links

- [OpenTelemetry Node.js](https://opentelemetry.io/docs/instrumentation/js/getting-started/nodejs/)
- [SigNoz Documentation](https://signoz.io/docs/)
- [Express Auto Instrumentation](https://opentelemetry.io/docs/instrumentation/js/libraries/)
- [OTLP Exporter](https://opentelemetry.io/docs/specs/otlp/)


# Solutions – Chapter 5: APM Concepts with SigNoz

## 1. Install **SigNoz locally** using Docker or Kubernetes.

<details>
<summary>Show Solution</summary>

**Docker Example:**
```bash
# Pull SigNoz Docker Compose setup
git clone https://github.com/SigNoz/signoz.git
cd signoz/deploy/
docker-compose up -d
```

**Kubernetes Example (using Helm):**

```bash
# Add SigNoz Helm repo
helm repo add signoz https://charts.signoz.io
helm repo update

# Install SigNoz
helm install signoz signoz/signoz --namespace signoz --create-namespace
```

After installation, access the UI at `http://localhost:3301` (Docker) or the Kubernetes service endpoint.

</details>

## 2. Instrument a Node.js Express application with OpenTelemetry.

<details>
<summary>Show Solution</summary>

**Step 1: Install dependencies**
```bash
npm init -y
npm install express
npm install @opentelemetry/api @opentelemetry/sdk-node @opentelemetry/auto-instrumentations-node @opentelemetry/exporter-otlp-http
```

**Step 2: Create `tracing.js`**
```javascript
const { NodeSDK } = require('@opentelemetry/sdk-node');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-http');

const sdk = new NodeSDK({
  traceExporter: new OTLPTraceExporter({
    url: 'http://localhost:4318/v1/traces',
  }),
  instrumentations: [getNodeAutoInstrumentations()],
});

sdk.start();

process.on('SIGTERM', () => {
  sdk.shutdown()
    .then(() => console.log('Tracing terminated'))
    .catch((error) => console.log('Error terminating tracing', error))
    .finally(() => process.exit(0));
});
```

**Step 3: Create `app.js`**
```javascript
const express = require('express');
const app = express();
const port = 3000;

app.get('/', (req, res) => {
  res.send('Hello World!');
});

app.get('/api/users', async (req, res) => {
  // Simulate some async work
  await new Promise(resolve => setTimeout(resolve, 100));
  res.json([{ id: 1, name: 'John' }]);
});

app.listen(port, () => {
  console.log(`Example app listening at http://localhost:${port}`);
});
```

**Step 4: Run the application**
```bash
node --require ./tracing.js app.js
```

Visit `http://localhost:3000` and check SigNoz UI for traces.

</details>

## 3. Create custom metrics for a sample application (e.g., user registrations, order completions).

<details>
<summary>Show Solution</summary>

**Step 1: Create `metrics.js`**
```javascript
const opentelemetry = require('@opentelemetry/api');
const { MeterProvider } = require('@opentelemetry/sdk-metrics');
const { PeriodicExportingMetricReader } = require('@opentelemetry/sdk-metrics');
const { Resource } = require('@opentelemetry/resources');
const { SemanticResourceAttributes } = require('@opentelemetry/semantic-conventions');
const { OTLPMetricExporter } = require('@opentelemetry/exporter-metrics-otlp-http');

// Configure resource
const resource = new Resource({
  [SemanticResourceAttributes.SERVICE_NAME]: 'user-service',
  [SemanticResourceAttributes.SERVICE_VERSION]: '1.0.0',
});

// Configure metric exporter
const metricExporter = new OTLPMetricExporter({
  url: 'http://localhost:4318/v1/metrics',
});

// Configure metric reader
const metricReader = new PeriodicExportingMetricReader({
  exporter: metricExporter,
  exportIntervalMillis: 10000,
});

// Setup meter provider
const meterProvider = new MeterProvider({
  resource,
  readers: [metricReader],
});

opentelemetry.metrics.setGlobalMeterProvider(meterProvider);

// Get a meter instance
const meter = opentelemetry.metrics.getMeter('user-service', '1.0.0');

// Define custom metrics
const userRegistrationCounter = meter.createCounter('users.registrations.total', {
  description: 'Total number of user registrations',
});

const activeUsersGauge = meter.createObservableGauge('users.active', {
  description: 'Number of currently active users',
});

const loginDurationHistogram = meter.createHistogram('auth.login.duration', {
  description: 'Time taken for user login in milliseconds',
  unit: 'ms',
});

const failedLoginCounter = meter.createCounter('auth.login.failed', {
  description: 'Total number of failed login attempts',
});

module.exports = {
  userRegistrationCounter,
  activeUsersGauge,
  loginDurationHistogram,
  failedLoginCounter,
};
```

**Step 2: Use metrics in your application**
```javascript
const express = require('express');
const {
  userRegistrationCounter,
  loginDurationHistogram,
  failedLoginCounter
} = require('./metrics');

const app = express();
app.use(express.json());

// Simulated user database
let users = [];
let activeUsers = new Set();

// Registration endpoint
app.post('/api/register', (req, res) => {
  const { username, email } = req.body;
  
  // Create user
  const user = { id: Date.now(), username, email };
  users.push(user);
  
  // Increment registration counter
  userRegistrationCounter.add(1, {
    method: 'email',
    source: req.headers['user-agent'].includes('Mobile') ? 'mobile' : 'web'
  });
  
  res.json({ success: true, userId: user.id });
});

// Login endpoint
app.post('/api/login', (req, res) => {
  const startTime = Date.now();
  const { username, password } = req.body;
  
  // Simulate authentication
  const user = users.find(u => u.username === username);
  
  if (user && password === 'password') {
    const duration = Date.now() - startTime;
    activeUsers.add(user.id);
    
    // Record login duration
    loginDurationHistogram.record(duration);
    
    res.json({ success: true, token: 'fake-jwt-token' });
  } else {
    // Increment failed login counter
    failedLoginCounter.add(1, {
      reason: !user ? 'user_not_found' : 'invalid_password'
    });
    
    res.status(401).json({ success: false, message: 'Invalid credentials' });
  }
});

app.listen(3000, () => {
  console.log('Server running on port 3000');
});
```

</details>

## 4. Send traces from a demo application to SigNoz.

<details>
<summary>Show Solution</summary>

Create a complete example with manual span creation:

```javascript
// app-instrumented.js
require('./tracing'); // Load tracing setup

const express = require('express');
const { trace } = require('@opentelemetry/api');
const tracer = trace.getTracer('demo-app', '1.0.0');

const app = express();

// Helper function to simulate work
async function simulateWork(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Express middleware to create spans
app.use((req, res, next) => {
  const span = tracer.startSpan(`${req.method} ${req.path}`);
  
  // Store span in request object
  req.span = span;
  
  res.on('finish', () => {
    span.setAttribute('http.status_code', res.statusCode);
    span.setAttribute('http.method', req.method);
    span.setAttribute('http.route', req.path);
    
    if (res.statusCode >= 400) {
      span.setStatus({ code: 1, message: 'Error' });
    }
    
    span.end();
  });
  
  next();
});

// Endpoints
app.get('/api/products', async (req, res) => {
  const span = tracer.startSpan('fetch_products', {
    parent: req.span
  });
  
  try {
    span.setAttribute('db.query', 'SELECT * FROM products');
    
    // Simulate database query
    await simulateWork(50);
    
    const products = [
      { id: 1, name: 'Product 1', price: 10.99 },
      { id: 2, name: 'Product 2', price: 20.99 }
    ];
    
    span.addEvent('products_fetched', { count: products.length });
    span.setStatus({ code: 0 });
    
    res.json(products);
  } catch (error) {
    span.recordException(error);
    span.setStatus({ code: 1, message: error.message });
    res.status(500).json({ error: error.message });
  } finally {
    span.end();
  }
});

app.get('/api/orders/:orderId', async (req, res) => {
  const orderId = req.params.orderId;
  
  // Create nested spans
  const orderSpan = tracer.startSpan('get_order', {
    attributes: { 'order.id': orderId }
  });
  
  const userSpan = tracer.startSpan('fetch_user', { parent: orderSpan });
  await simulateWork(30);
  userSpan.end();
  
  const itemsSpan = tracer.startSpan('fetch_order_items', { parent: orderSpan });
  await simulateWork(40);
  itemsSpan.end();
  
  const order = {
    id: orderId,
    userId: 123,
    items: ['item1', 'item2'],
    total: 45.98
  };
  
  orderSpan.setStatus({ code: 0 });
  orderSpan.end();
  
  res.json(order);
});

app.listen(3000, () => {
  console.log('Server running on port 3000');
});
```

Run: `node --require ./tracing.js app-instrumented.js`

</details>

## 5. Set up dashboards in SigNoz to visualize your custom metrics.

<details>
<summary>Show Solution</summary>

**Steps to create dashboards in SigNoz:**

1. **Access SigNoz UI**: Navigate to `http://localhost:3301`

2. **Go to Dashboards**: Click on "Dashboards" in the left sidebar

3. **Create New Dashboard**: Click "New Dashboard" → Enter name (e.g., "User Metrics Dashboard")

4. **Add Panel for User Registrations**:
   - Click "Add Panel" → "Time Series"
   - Query: `sum(users_registrations_total)` or `rate(users_registrations_total[5m])`
   - Title: "User Registrations Rate"

5. **Add Panel for Login Duration**:
   - Panel Type: "Histogram" or "Time Series"
   - Query: `histogram_quantile(0.95, rate(auth_login_duration_bucket[5m]))`
   - Title: "95th Percentile Login Duration"

6. **Add Panel for Failed Logins**:
   - Panel Type: "Time Series"
   - Query: `sum(rate(auth_login_failed[5m]))`
   - Title: "Failed Login Attempts Rate"

7. **Configure Alerts**:
   - Go to "Alerts" section
   - Create alert rule:
     - Alert Name: "High Failed Login Rate"
     - Metric: `sum(rate(auth_login_failed[5m]))`
     - Threshold: `> 10` (failures per 5 minutes)
     - Action: Send notification

**Tips:**
- Use PromQL queries to aggregate metrics
- Group by labels (e.g., `by (method, source)`)
- Set up refresh intervals for real-time monitoring
- Use heatmaps for histogram metrics

</details>

## 6. Identify a bottleneck in a multi-service application using SigNoz traces.

<details>
<summary>Show Solution</summary>

**Example Multi-Service Application:**

```javascript
// service-a.js - API Gateway
const express = require('express');
const axios = require('axios');
require('./tracing');

const app = express();

app.get('/api/user/:userId/orders', async (req, res) => {
  const startTime = Date.now();
  
  try {
    // Call user service
    const userResponse = await axios.get(`http://localhost:3001/users/${req.params.userId}`);
    
    // Call order service
    const ordersResponse = await axios.get(`http://localhost:3002/orders?userId=${req.params.userId}`);
    
    res.json({
      user: userResponse.data,
      orders: ordersResponse.data
    });
    
    console.log(`Total time: ${Date.now() - startTime}ms`);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.listen(3000);

// service-b.js - User Service
const express = require('express');
const axios = require('axios');
require('./tracing');

const app = express();

app.get('/users/:userId', async (req, res) => {
  // Simulate slow database query
  await new Promise(resolve => setTimeout(resolve, 500));
  
  res.json({ id: req.params.userId, name: 'John Doe' });
});

app.listen(3001);

// service-c.js - Order Service
const express = require('express');
require('./tracing');

const app = express();

app.get('/orders', async (req, res) => {
  // Simulate quick lookup
  await new Promise(resolve => setTimeout(resolve, 50));
  
  res.json([
    { id: 1, total: 100 },
    { id: 2, total: 200 }
  ]);
});

app.listen(3002);
```

**How to identify bottlenecks:**

1. **View Trace Map**: 
   - Navigate to SigNoz → "Services" → "Service Map"
   - See dependency graph and flow

2. **Analyze Span Duration**:
   - Go to "Traces" → Find traces for `/api/user/:userId/orders`
   - Expand the trace to see span waterfall
   - Identify the slowest span (likely user service at ~500ms)

3. **Filter by Duration**:
   - Use filter: `duration > 400ms`
   - Shows only slow traces

4. **Compare P95/P99**:
   - Dashboard → Service metrics
   - View p95/p99 latencies per service
   - User service p95 = 500ms indicates consistent slow response

5. **Root Cause**:
   - Slow database query in user service (500ms)
   - Recommendation: Add caching, optimize query, or index database

</details>

## 7. Bonus: Research how SigNoz differs from **Datadog** or **New Relic** in terms of cost and features.

<details>
<summary>Show Solution</summary>

* **SigNoz:**

  * Open-source and self-hosted.
  * No subscription cost for software (only infra).
  * Built on OpenTelemetry → supports metrics, logs, traces.
  * Community support with commercial support available.
  * Requires infrastructure management.

* **Datadog / New Relic:**

  * Commercial SaaS with subscription fees.
  * Fully managed with rich integrations.
  * Often easier to start but can be expensive at scale.
  * Pay-per-data-ingested model can become costly.
  * Enterprise features require higher-tier plans.

**Summary:** SigNoz is cost-effective and open-source but requires infrastructure setup. Datadog/New Relic are turnkey solutions with higher cost.

</details>

## 8. Bonus: Implement distributed tracing across multiple Node.js services.

<details>
<summary>Show Solution</summary>

**Key setup for distributed tracing:**

1. **Ensure consistent trace context propagation** (automatically handled by OpenTelemetry)

2. **Configure Sampler** (optional) in `tracing.js`:
```javascript
const { NodeSDK } = require('@opentelemetry/sdk-node');
const { TraceIdRatioBasedSampler } = require('@opentelemetry/core');

const sdk = new NodeSDK({
  sampler: new TraceIdRatioBasedSampler(0.1), // Sample 10% of traces
  // ... rest of config
});
```

3. **Add baggage for context propagation**:
```javascript
const { baggage, propagation } = require('@opentelemetry/api');

// Set baggage in service A
baggage.setValue('user.id', userId);
baggage.setValue('request.source', 'mobile');

// Read baggage in service B
const userId = baggage.getValue('user.id');
```

4. **Run all services** and make requests across them to see complete traces in SigNoz.

</details>
# Chapter 5: APM Concepts with SigNoz

## 5.1 What is APM?
APM (Application Performance Monitoring) is the practice of monitoring and managing the performance and availability of software applications.  
It helps SREs and developers understand:
- How requests perform across services  
- Where bottlenecks exist  
- How users experience the application  

**Analogy:** APM is like having CCTV cameras inside a restaurant kitchen. Instead of just knowing customers are waiting, you can see *why* food is delayed (e.g., slow chef, missing ingredients).

## 5.2 Key Features of APM
- **Request Tracing**: Follow a request across multiple services.  
- **Error Tracking**: Identify failing services or endpoints.  
- **Performance Metrics**: Response time, throughput, error rate.  
- **Dashboards**: Visualize service health in real time.  

## 5.3 Introduction to SigNoz
SigNoz is an open-source APM and observability platform. It provides metrics, logs, and traces in one place.  
- Built on OpenTelemetry  
- Alternative to commercial APM tools (like Datadog, New Relic)  
- Self-hosted, making it great for cost-sensitive teams  

## 5.4 How Data Flows into SigNoz
1. Application generates telemetry data (metrics, logs, traces).  
2. OpenTelemetry Collector receives the data.  
3. Collector exports the data to SigNoz backend.  
4. SigNoz UI visualizes and analyzes the data.  

## 5.5 Example: OpenTelemetry Collector Sending Data to SigNoz
receivers:  
  otlp:  
    protocols:  
      grpc:  
      http:  

exporters:  
  otlp:  
    endpoint: "http://localhost:4317"  

service:  
  pipelines:  
    traces:  
      receivers: [otlp]  
      exporters: [otlp]  

## 5.6 Real-World Scenario
Imagine a payment service in a microservices architecture.  
- APM shows that 20% of requests are taking 5 seconds instead of 200ms.  
- Traces reveal the delay is caused by the database query.  
- The SRE team can then optimize the database or add caching.  

## 5.7 Node.js Instrumentation with OpenTelemetry & SigNoz

### 5.7.1 Overview
OpenTelemetry (OTel) provides instrumentation libraries for Node.js to collect traces, metrics, and logs from your applications. When combined with SigNoz, you get a complete observability solution.

### 5.7.2 Installation

**Install Required Packages:**
```bash
npm install @opentelemetry/api
npm install @opentelemetry/sdk-node
npm install @opentelemetry/auto-instrumentations-node
npm install @opentelemetry/exporter-otlp-http
```

**Or using Yarn:**
```bash
yarn add @opentelemetry/api @opentelemetry/sdk-node @opentelemetry/auto-instrumentations-node @opentelemetry/exporter-otlp-http
```

### 5.7.3 Basic Setup (Automatic Instrumentation)

Create a file `tracing.js` at the root of your Node.js application:

```javascript
const { NodeSDK } = require('@opentelemetry/sdk-node');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-otlp-http');

const sdk = new NodeSDK({
  traceExporter: new OTLPTraceExporter({
    url: 'http://localhost:4318/v1/traces', // SigNoz endpoint
  }),
  instrumentations: [getNodeAutoInstrumentations()],
});

// Initialize the SDK
sdk.start();

// Gracefully shutdown the SDK
process.on('SIGTERM', () => {
  sdk.shutdown()
    .then(() => console.log('Tracing terminated'))
    .catch((error) => console.log('Error terminating tracing', error))
    .finally(() => process.exit(0));
});
```

**Start Your Application:**
```bash
# Load tracing.js before your main application
node --require ./tracing.js app.js
```

### 5.7.4 Custom Metrics

Creating custom metrics allows you to track business-specific metrics that matter to your application.

**Example: Custom Metrics for an E-commerce Application**

```javascript
const opentelemetry = require('@opentelemetry/api');
const { MeterProvider } = require('@opentelemetry/sdk-metrics');
const { PeriodicExportingMetricReader } = require('@opentelemetry/sdk-metrics');
const { Resource } = require('@opentelemetry/resources');
const { SemanticResourceAttributes } = require('@opentelemetry/semantic-conventions');
const { OTLPMetricExporter } = require('@opentelemetry/exporter-metrics-otlp-http');

// Configure resource
const resource = new Resource({
  [SemanticResourceAttributes.SERVICE_NAME]: 'ecommerce-api',
  [SemanticResourceAttributes.SERVICE_VERSION]: '1.0.0',
});

// Configure metric exporter
const metricExporter = new OTLPMetricExporter({
  url: 'http://localhost:4318/v1/metrics', // SigNoz endpoint
});

// Configure metric reader
const metricReader = new PeriodicExportingMetricReader({
  exporter: metricExporter,
  exportIntervalMillis: 10000, // Export every 10 seconds
});

// Setup meter provider
const meterProvider = new MeterProvider({
  resource,
  readers: [metricReader],
});

// Set as global meter provider
opentelemetry.metrics.setGlobalMeterProvider(meterProvider);

// Get a meter instance
const meter = opentelemetry.metrics.getMeter('ecommerce-app', '1.0.0');

// Define custom metrics
const orderCounter = meter.createCounter('orders.total', {
  description: 'Total number of orders placed',
});

const cartValueGauge = meter.createObservableGauge('cart.value', {
  description: 'Current value of items in cart',
});

const orderProcessingTime = meter.createHistogram('order.processing_time', {
  description: 'Time taken to process an order in milliseconds',
  unit: 'ms',
});

// Export metrics for use in your application
module.exports = {
  orderCounter,
  cartValueGauge,
  orderProcessingTime,
};
```

**Using Custom Metrics in Your Application:**

```javascript
const express = require('express');
const { orderCounter, orderProcessingTime } = require('./metrics');

const app = express();

app.post('/api/orders', async (req, res) => {
  const startTime = Date.now();
  
  try {
    // Process order logic here
    const order = await processOrder(req.body);
    
    // Increment order counter
    orderCounter.add(1, { 
      status: 'success',
      payment_method: order.paymentMethod 
    });
    
    const processingTime = Date.now() - startTime;
    
    // Record processing time
    orderProcessingTime.record(processingTime, {
      payment_method: order.paymentMethod,
      priority: order.priority || 'normal'
    });
    
    res.json({ success: true, orderId: order.id });
  } catch (error) {
    // Still increment counter for failed orders
    orderCounter.add(1, { 
      status: 'failed',
      error_type: error.name 
    });
    
    res.status(500).json({ error: error.message });
  }
});
```

### 5.7.5 Manual Span Creation

For more granular control, you can manually create spans:

```javascript
const { trace } = require('@opentelemetry/api');
const tracer = trace.getTracer('payment-service', '1.0.0');

async function processPayment(orderId) {
  // Start a new span
  const span = tracer.startSpan('process_payment');
  
  try {
    span.setAttribute('order.id', orderId);
    span.setAttribute('payment.amount', order.amount);
    
    // Simulate payment processing
    const result = await chargeCreditCard(order);
    
    span.addEvent('payment_charged', {
      transaction_id: result.transactionId,
    });
    
    span.setStatus({ code: opentelemetry.SpanStatusCode.OK });
    
    return result;
  } catch (error) {
    span.recordException(error);
    span.setStatus({ 
      code: opentelemetry.SpanStatusCode.ERROR,
      message: error.message 
    });
    throw error;
  } finally {
    // End the span
    span.end();
  }
}
```

### 5.7.6 Environment Variables Configuration

For easier configuration, use environment variables:

```javascript
// .env
OTEL_SERVICE_NAME=ecommerce-api
OTEL_SERVICE_VERSION=1.0.0
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
OTEL_RESOURCE_ATTRIBUTES=environment=production,region=us-east-1
OTEL_LOG_LEVEL=info
```

### 5.7.7 Common Metrics in Production

**Application Metrics:**
- Request rate (requests/second)
- Response time (p50, p95, p99)
- Error rate (percentage)
- Throughput (bytes/second)

**Business Metrics:**
- User signups per day
- Orders placed per hour
- Revenue per transaction
- Cart abandonment rate

**Infrastructure Metrics:**
- CPU usage
- Memory consumption
- Database connection pool size
- Cache hit rate

### 5.7.8 Best Practices for Node.js Instrumentation

1. **Use Automatic Instrumentation**: Enable auto-instrumentation for common libraries (Express, HTTP, MySQL, etc.)
2. **Instrument Key Operations**: Add manual spans for critical business logic
3. **Add Context**: Use attributes and events to provide context in traces
4. **Monitor Resource Usage**: Track memory, CPU, and other resource metrics
5. **Set Up Alerts**: Configure alerts in SigNoz for critical metrics
6. **Sample Strategically**: For high-traffic apps, use sampling to reduce overhead

### 5.7.9 Viewing Data in SigNoz

After instrumenting your Node.js application:

1. **Traces**: Navigate to "Traces" tab to see request traces across services
2. **Metrics**: Check "Dashboards" for custom and application metrics
3. **Services**: View service health and dependencies under "Services"
4. **Alerts**: Set up alerts based on your custom metrics

## 5.8 Exercises
1. Install SigNoz locally using Docker or Kubernetes.  
2. Instrument a Node.js Express application with OpenTelemetry.  
3. Create custom metrics for a sample application (e.g., user registrations, order completions).  
4. Send traces from a demo application to SigNoz.  
5. Set up dashboards in SigNoz to visualize your custom metrics.  
6. Identify a bottleneck in a multi-service application using SigNoz traces.  

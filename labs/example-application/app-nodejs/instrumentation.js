/**
 * ⚡ OPENTELEMETRY INSTRUMENTATION FOR SIGNOZ
 *
 * This file automatically configures collection of:
 * - Traces (request lifecycles)
 * - Metrics (performance counters)
 * - Logs (application events)
 *
 * When you preload this file with `-r`, it:
 * 1. Boots the OpenTelemetry SDK
 * 2. Enables auto-instrumentation for common libraries
 * 3. Ships telemetry to SigNoz through the OTel Collector
 */

const { NodeSDK } = require('@opentelemetry/sdk-node');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-grpc');
const { Resource } = require('@opentelemetry/resources');
const { SemanticResourceAttributes } = require('@opentelemetry/semantic-conventions');

/**
 * 🔧 OPEN TELEMETRY SDK CONFIGURATION
 */
const sdk = new NodeSDK({
  /**
   * 📦 RESOURCE METADATA – identifies this service
   *
   * Semantic attributes help SigNoz:
   * - Group telemetry by service
   * - Filter and search effectively
   * - Display descriptive labels in the UI
   */
  resource: new Resource({
    [SemanticResourceAttributes.SERVICE_NAME]: 'signoz-example-nodejs',
    [SemanticResourceAttributes.SERVICE_VERSION]: '1.0.0',
    [SemanticResourceAttributes.DEPLOYMENT_ENVIRONMENT]: 'development',
  }),

  /**
   * 🔄 TRACE EXPORTER
   *
   * Sends traces to the OTel Collector.
   * - Protocol: OTLP over gRPC
   * - Endpoint: Collector listening on 4317
   */
  traceExporter: new OTLPTraceExporter({
    url: 'http://localhost:4317',
    // Optional: add headers if your collector enforces auth
    // headers: { Authorization: 'Bearer <token>' },
  }),

  /**
   * 📊 METRIC EXPORTER
   *
   * Metrics are handled automatically by the SDK for this sample,
   * so no dedicated exporter is required here.
   */

  /**
   * ⚡ AUTO INSTRUMENTATION
   *
   * This enables instrumentation for:
   * ✅ HTTP/HTTPS clients and servers
   * ✅ Express
   * ✅ PostgreSQL, MySQL, MongoDB
   * ✅ Redis
   * ✅ GraphQL
   * ✅ …and many more integrations!
   *
   * No manual instrumentation required for common libraries.
   */
  instrumentations: [
    getNodeAutoInstrumentations({
      // Disable instrumentation you do not need
      '@opentelemetry/instrumentation-fs': {
        enabled: false, // Filesystem instrumentation is rarely useful here
      },
    }),
  ],

  /**
   * 📝 LOGGER
   *
   * Configure OpenTelemetry logging (debug, info, warn, error).
   * The resource already sets the service name, so no need to override it here.
   */
});

/**
 * ▶️ START THE SDK
 *
 * From this point forward, everything is traced automatically.
 */
sdk.start();
console.log('⚡ OpenTelemetry SDK initialized');
console.log('📊 Sending traces to: http://localhost:4317');
console.log('🔍 View telemetry at: http://localhost:8080\n');

/**
 * 🛑 GRACEFUL SHUTDOWN
 *
 * Ensure telemetry is flushed when the app stops.
 */
process.on('SIGTERM', () => {
  sdk.shutdown()
    .then(() => console.log('\n🔌 Telemetry shut down'))
    .catch((error) => console.log('\n❌ Error during telemetry shutdown:', error))
    .finally(() => process.exit(0));
});

module.exports = sdk;

/**
 * 📚 KEY CONCEPTS
 *
 * 1. TRACE: Follows a single request as it flows through the system
 * 2. SPAN: A timed unit of work within a trace (DB query, external API call)
 * 3. METRIC: Numeric measurement over time
 * 4. ATTRIBUTE: Metadata attached to spans/traces
 * 5. CONTEXT: Correlates telemetry across services
 *
 * 🎯 WHAT YOU GET
 *
 * - 🔍 Traces: Understand each request’s journey
 * - 📊 Metrics: Monitor performance, errors, throughput
 * - 🐛 Debugging: Spot bottlenecks and failures quickly
 * - 📈 Alerting: Configure automated alerts in SigNoz
 *
 * 🚀 QUICK START
 *
 * 1. Run: npm install
 * 2. Run: npm start
 * 3. Visit: http://localhost:8080 (SigNoz UI)
 * 4. Generate traffic and explore live telemetry!
 */


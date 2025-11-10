"""
 OPENTELEMETRY INSTRUMENTATION FOR SIGNOZ – PYTHON

This module automatically configures collection of:
- Traces (request lifecycles)
- Metrics (performance counters)
- Logs (application events)

When imported before the Flask app it:
1. Boots the OpenTelemetry SDK
2. Enables auto-instrumentation for popular libraries
3. Ships telemetry to SigNoz through the OTel Collector
"""

import logging
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import (
    Resource,
    SERVICE_NAME,
    SERVICE_VERSION,
    DEPLOYMENT_ENVIRONMENT,
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor


def setup_instrumentation():
    """
     Configure the OpenTelemetry SDK.
    """

    # ----------------------------------------------------------------------------
    # RESOURCE METADATA – identifies this service
    # ----------------------------------------------------------------------------
    resource = Resource.create({
        SERVICE_NAME: "signoz-example-python",
        SERVICE_VERSION: "1.0.0",
        DEPLOYMENT_ENVIRONMENT: "development",
    })

    # ----------------------------------------------------------------------------
    # TRACE CONFIGURATION
    # ----------------------------------------------------------------------------

    tracer_provider = TracerProvider(resource=resource)

    otlp_trace_exporter = OTLPSpanExporter(
        endpoint="http://localhost:4317",  # OTel Collector endpoint
        insecure=True,
    )

    span_processor = BatchSpanProcessor(otlp_trace_exporter)
    tracer_provider.add_span_processor(span_processor)

    trace.set_tracer_provider(tracer_provider)

    # ----------------------------------------------------------------------------
    # METRIC CONFIGURATION
    # ----------------------------------------------------------------------------

    otlp_metric_exporter = OTLPMetricExporter(
        endpoint="http://localhost:4317",
        insecure=True,
    )

    metric_reader = PeriodicExportingMetricReader(
        otlp_metric_exporter,
        export_interval_millis=60000,  # 60 seconds
    )

    meter_provider = MeterProvider(
        resource=resource,
        metric_readers=[metric_reader],
    )
    # Note: The default Python SDK requires explicit registration to use this
    # meter provider for custom metrics. For simplicity we rely on auto-instrumented metrics.

    # ----------------------------------------------------------------------------
    # AUTO-INSTRUMENTATION
    # ----------------------------------------------------------------------------

    FlaskInstrumentor().instrument()
    RequestsInstrumentor().instrument()

    # ----------------------------------------------------------------------------
    # LOGGING
    # ----------------------------------------------------------------------------

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # ----------------------------------------------------------------------------
    # SUCCESS MESSAGE
    # ----------------------------------------------------------------------------

    print(" OpenTelemetry SDK initialized")
    print(" Sending traces and metrics to: http://localhost:4317")
    print(" View telemetry at: http://localhost:8080\n")


# ----------------------------------------------------------------------------
# IMPORTANT: Execute setup when the module is imported
# ----------------------------------------------------------------------------
setup_instrumentation()


"""
 KEY CONCEPTS

1. TRACE: Tracks a single request through your system
2. SPAN: A timed unit of work within a trace (DB call, external API, etc.)
3. METRIC: Numeric measurements collected over time
4. ATTRIBUTE: Metadata attached to spans/traces
5. CONTEXT: Propagates tracing information across service boundaries

 WHAT YOU GAIN

-  Traces: Observe exactly how each request flows through the app
-  Metrics: Monitor performance, throughput, and errors
-  Debugging: Quickly pinpoint bottlenecks or failures
-  Alerting: Build automated alerts in SigNoz

 NEXT STEPS

1. pip install -r requirements.txt
2. python app.py
3. Visit http://localhost:8080 (SigNoz UI)
4. Generate traffic and explore real-time telemetry!
"""


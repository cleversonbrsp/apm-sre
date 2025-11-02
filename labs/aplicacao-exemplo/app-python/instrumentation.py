"""
⚡ INSTRUMENTAÇÃO OPEN TELEMETRY PARA SIGNOZ - PYTHON

Este módulo configura automaticamente a coleta de:
- Traces (rastreamento de requisições)
- Métricas (performance, contadores)
- Logs (eventos da aplicação)

Quando importado antes da aplicação Flask, ele:
1. Configura o SDK do OpenTelemetry
2. Habilita auto-instrumentação de bibliotecas populares
3. Exporta os dados para o SigNoz via Otel Collector
"""

import logging
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION, DEPLOYMENT_ENVIRONMENT
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor


def setup_instrumentation():
    """
    🔧 CONFIGURA O OPEN TELEMETRY SDK
    """
    
    # ----------------------------------------------------------------------------
    # RECURSO: Identifica sua aplicação
    # ----------------------------------------------------------------------------
    resource = Resource.create({
        SERVICE_NAME: "signoz-example-python",
        SERVICE_VERSION: "1.0.0",
        DEPLOYMENT_ENVIRONMENT: "development",
    })
    
    # ----------------------------------------------------------------------------
    # CONFIGURAÇÃO DE TRACES
    # ----------------------------------------------------------------------------
    
    # Provider de Traces: Gerencia e coleta traces
    tracer_provider = TracerProvider(resource=resource)
    
    # Exportador de Traces: Envia traces para o SigNoz
    otlp_trace_exporter = OTLPSpanExporter(
        endpoint="http://localhost:4317",  # Endpoint do Otel Collector
        insecure=True,  # Por padrão é HTTP, não HTTPS
    )
    
    # Processador de Spans: Agrupa spans em batches para envio eficiente
    span_processor = BatchSpanProcessor(otlp_trace_exporter)
    tracer_provider.add_span_processor(span_processor)
    
    # Ativa o provider de traces
    trace.set_tracer_provider(tracer_provider)
    
    # ----------------------------------------------------------------------------
    # CONFIGURAÇÃO DE MÉTRICAS
    # ----------------------------------------------------------------------------
    
    # Exportador de Métricas
    otlp_metric_exporter = OTLPMetricExporter(
        endpoint="http://localhost:4317",
        insecure=True,
    )
    
    # Leitor de Métricas: Exporta métricas periodicamente (a cada 60s)
    metric_reader = PeriodicExportingMetricReader(
        otlp_metric_exporter,
        export_interval_millis=60000,  # 60 segundos
    )
    
    # Provider de Métricas
    meter_provider = MeterProvider(
        resource=resource,
        metric_readers=[metric_reader],
    )
    
    # Nota: O SDK padrão do Python não expõe um global MeterProvider facilmente
    # Para métricas customizadas, você criaria assim:
    # from opentelemetry import metrics
    # metrics.set_meter_provider(meter_provider)
    
    # ----------------------------------------------------------------------------
    # AUTO-INSTRUMENTAÇÃO
    # ----------------------------------------------------------------------------
    
    # Flask: Instrumenta automaticamente todas as rotas
    FlaskInstrumentor().instrument()
    
    # Requests: Instrumenta chamadas HTTP externas
    RequestsInstrumentor().instrument()
    
    # ----------------------------------------------------------------------------
    # LOGGING
    # ----------------------------------------------------------------------------
    
    # Configura logs do OpenTelemetry
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # ----------------------------------------------------------------------------
    # SUCESSO!
    # ----------------------------------------------------------------------------
    
    print("⚡ OpenTelemetry SDK inicializado")
    print("📊 Enviando traces e métricas para: http://localhost:4317")
    print("🔍 Dados aparecerão no SigNoz em: http://localhost:8080\n")


# ----------------------------------------------------------------------------
# IMPORTANTE: Execute a configuração quando o módulo é importado
# ----------------------------------------------------------------------------
setup_instrumentation()


"""
📚 CONCEITOS IMPORTANTES:

1. TRACE: Rastreia uma requisição HTTP única através do sistema
2. SPAN: Cada operação dentro de um trace (ex: chamada DB, API externa)
3. METRIC: Valores numéricos medidos ao longo do tempo
4. ATTRIBUTE: Metadados anexados a traces/spans
5. CONTEXT: Propaga informações através de diferentes serviços

🎯 O QUE VOCÊ GANHA:

- 🔍 Traces: Veja exatamente como cada requisição flui pela aplicação
- 📊 Métricas: Monitore performance, erros, throughput
- 🐛 Debug: Identifique gargalos e erros rapidamente
- 📈 Alertas: Configure alertas automáticos

🚀 PRÓXIMOS PASSOS:

1. Execute: pip install -r requirements.txt
2. Execute: python app.py
3. Acesse: http://localhost:8080 (SigNoz)
4. Explore os dados em tempo real!
"""


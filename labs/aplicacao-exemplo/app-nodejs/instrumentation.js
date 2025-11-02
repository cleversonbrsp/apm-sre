/**
 * ⚡ INSTRUMENTAÇÃO OPEN TELEMETRY PARA SIGNOZ
 * 
 * Este arquivo configura automaticamente a coleta de:
 * - Traces (rastreamento de requisições)
 * - Métricas (performance, contadores)
 * - Logs (eventos da aplicação)
 * 
 * Quando você importa este arquivo com -r, ele:
 * 1. Configura o SDK do OpenTelemetry
 * 2. Habilita auto-instrumentação de bibliotecas populares
 * 3. Exporta os dados para o SigNoz via Otel Collector
 */

const { NodeSDK } = require('@opentelemetry/sdk-node');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-grpc');
const { Resource } = require('@opentelemetry/resources');
const { SemanticResourceAttributes } = require('@opentelemetry/semantic-conventions');

/**
 * 🔧 CONFIGURAÇÃO DO OPEN TELEMETRY SDK
 */
const sdk = new NodeSDK({
  /**
   * 📦 RECURSO: Identifica sua aplicação
   * 
   * Os atributos semânticos ajudam o SigNoz a:
   * - Identificar de qual serviço vêm os dados
   * - Filtrar e agrupar dados
   * - Mostrar informações úteis na UI
   */
  resource: new Resource({
    [SemanticResourceAttributes.SERVICE_NAME]: 'signoz-example-nodejs',
    [SemanticResourceAttributes.SERVICE_VERSION]: '1.0.0',
    [SemanticResourceAttributes.DEPLOYMENT_ENVIRONMENT]: 'development',
  }),

  /**
   * 🔄 EXPORTADOR DE TRACES
   * 
   * Onde enviar os traces (rastreamento de requisições)
   * - OTLP: Open Telemetry Protocol
   * - gRPC: Protocolo de comunicação
   * - Endpoint: Otel Collector na porta 4317
   */
  traceExporter: new OTLPTraceExporter({
    url: 'http://localhost:4317', // Endpoint do Otel Collector
    // Opcional: adicionar headers de autenticação se necessário
    // headers: { 'Authorization': 'Bearer token' }
  }),

  /**
   * 📊 EXPORTADOR DE MÉTRICAS
   * 
   * Métricas são coletadas automaticamente pelo SDK
   * Não é necessário configurar um exportador separado para esta demo
   */

  /**
   * ⚡ AUTO-INSTRUMENTAÇÃO
   * 
   * Isso habilita automaticamente a instrumentação para:
   * ✅ HTTP/HTTPS requests
   * ✅ Express framework
   * ✅ PostgreSQL, MySQL, MongoDB
   * ✅ Redis
   * ✅ GraphQL
   * ✅ E muito mais!
   * 
   * Você não precisa modificar seu código manualmente!
   */
  instrumentations: [
    getNodeAutoInstrumentations({
      // Pode desabilitar instrumentações específicas se não usar
      '@opentelemetry/instrumentation-fs': {
        enabled: false, // Desabilita instrumentação de filesystem
      },
      // '@opentelemetry/instrumentation-express': {
      //   enabled: true,
      // },
    }),
  ],

  /**
   * 📝 LOGGER
   * 
   * Configura logs do OpenTelemetry (debug, info, warn, error)
   */
  // serviceName: 'signoz-example-nodejs', // Opcional, já definido no Resource
});

/**
 * ▶️ INICIALIZA O SDK
 * 
 * Esta linha ATIVA a instrumentação.
 * Tudo que acontecer após isso será automaticamente rastreado!
 */
sdk.start();
console.log('⚡ OpenTelemetry SDK inicializado');
console.log('📊 Enviando traces e métricas para: http://localhost:4317');
console.log('🔍 Dados aparecerão no SigNoz em: http://localhost:8080\n');

/**
 * 🛑 LIMPEZA AO ENCERRAR
 * 
 * Quando a aplicação é encerrada, desliga o SDK corretamente
 */
process.on('SIGTERM', () => {
  sdk.shutdown()
    .then(() => console.log('\n🔌 Telemetria encerrada'))
    .catch((error) => console.log('\n❌ Erro ao encerrar telemetria:', error))
    .finally(() => process.exit(0));
});

module.exports = sdk;

/**
 * 📚 CONCEITOS IMPORTANTES:
 * 
 * 1. TRACE: Rastreia uma requisição HTTP única através do sistema
 * 2. SPAN: Cada operação dentro de um trace (ex: chamada DB, API externa)
 * 3. METRIC: Valores numéricos medidos ao longo do tempo
 * 4. ATTRIBUTE: Metadados anexados a traces/spans
 * 5. CONTEXT: Propaga informações através de diferentes serviços
 * 
 * 🎯 O QUE VOCÊ GANHA:
 * 
 * - 🔍 Traces: Veja exatamente como cada requisição flui pela aplicação
 * - 📊 Métricas: Monitore performance, erros, throughput
 * - 🐛 Debug: Identifique gargalos e erros rapidamente
 * - 📈 Alertas: Configure alertas automáticos
 * 
 * 🚀 PRÓXIMOS PASSOS:
 * 
 * 1. Execute: npm install
 * 2. Execute: npm start
 * 3. Acesse: http://localhost:8080 (SigNoz)
 * 4. Explore os dados em tempo real!
 */


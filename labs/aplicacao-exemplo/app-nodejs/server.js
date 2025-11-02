/**
 * 🌐 APLICAÇÃO EXEMPLO NODE.JS + EXPRESS
 * 
 * Esta aplicação demonstra uma API RESTful com:
 * - Rotas de API
 * - Simulação de banco de dados
 * - Diferentes tipos de operações
 * - Alguns endpoints com propósito de mostrar observabilidade
 */

const express = require('express');
const app = express();

// Middleware para parsing JSON
app.use(express.json());

/**
 * 📝 IMPORTANTE: A instrumentação foi carregada antes deste arquivo
 * Via: node -r ./instrumentation.js server.js
 * 
 * Isso significa que TODAS as requisições HTTP já estão sendo rastreadas!
 */

// Mock database
let users = [
  { id: 1, name: 'Alice Silva', email: 'alice@example.com', role: 'admin' },
  { id: 2, name: 'Bob Souza', email: 'bob@example.com', role: 'user' },
  { id: 3, name: 'Carol Costa', email: 'carol@example.com', role: 'user' },
];

let products = [
  { id: 1, name: 'Laptop', price: 2999.99, stock: 15 },
  { id: 2, name: 'Mouse', price: 89.90, stock: 50 },
  { id: 3, name: 'Teclado', price: 199.90, stock: 30 },
];

// ============================================================================
// ROTAS DA API
// ============================================================================

/**
 * 🏠 ROTA RAIZ
 * 
 * Página inicial com informações sobre a API
 */
app.get('/', (req, res) => {
  res.json({
    message: '🚀 API Node.js instrumentada com OpenTelemetry',
    version: '1.0.0',
    endpoints: {
      health: 'GET /api/health',
      users: {
        list: 'GET /api/users',
        get: 'GET /api/users/:id',
        create: 'POST /api/users'
      },
      products: 'GET /api/products (20% chance de erro)',
      slow: 'GET /api/slow (operação lenta)',
      redirect: 'GET /api/redirect-demo'
    },
    signoz: 'http://localhost:8080',
    instrumentation: 'OpenTelemetry auto-instrumentado'
  });
});

/**
 * 🏥 HEALTH CHECK
 * 
 * Endpoint básico para verificar se a aplicação está rodando
 * Rastreado automaticamente pelo OpenTelemetry!
 */
app.get('/api/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
  });
});

/**
 * 👥 LISTAR USUÁRIOS
 * 
 * Retorna todos os usuários
 * Mostra traces de operações bem-sucedidas
 */
app.get('/api/users', (req, res) => {
  console.log('📋 Listando todos os usuários');
  
  // Simula delay de banco de dados
  setTimeout(() => {
    res.json({
      count: users.length,
      users: users,
    });
  }, 100);
});

/**
 * 👤 BUSCAR USUÁRIO POR ID
 * 
 * Retorna um usuário específico
 * Mostra traces com atributos customizados
 */
app.get('/api/users/:id', (req, res) => {
  const id = parseInt(req.params.id);
  const user = users.find(u => u.id === id);
  
  console.log(`🔍 Buscando usuário ID: ${id}`);
  
  if (!user) {
    return res.status(404).json({
      error: 'Usuário não encontrado',
      requestedId: id,
    });
  }
  
  res.json(user);
});

/**
 * ➕ CRIAR NOVO USUÁRIO
 * 
 * Adiciona um novo usuário
 * Mostra traces de operações de escrita
 */
app.post('/api/users', (req, res) => {
  const { name, email, role } = req.body;
  
  console.log(`➕ Criando novo usuário: ${name} (${email})`);
  
  if (!name || !email) {
    return res.status(400).json({
      error: 'Nome e email são obrigatórios',
    });
  }
  
  const newUser = {
    id: users.length + 1,
    name,
    email,
    role: role || 'user',
  };
  
  users.push(newUser);
  
  res.status(201).json({
    message: 'Usuário criado com sucesso',
    user: newUser,
  });
});

/**
 * 🛍️ LISTAR PRODUTOS (COM ERRO)
 * 
 * Este endpoint simula um erro ocasional
 * Perfeito para ver rastreamento de erros no SigNoz!
 */
app.get('/api/products', (req, res) => {
  console.log('🛍️ Listando produtos...');
  
  // Simula 20% de chance de erro
  if (Math.random() < 0.2) {
    console.error('❌ Erro ao buscar produtos do banco');
    return res.status(500).json({
      error: 'Erro interno ao buscar produtos',
      message: 'Falha na conexão com o banco de dados',
    });
  }
  
  res.json({
    count: products.length,
    products: products,
  });
});

/**
 * 🐌 ENDPOINT LENTO
 * 
 * Simula uma operação lenta (ex: query complexa, integração externa)
 * Perfeito para ver traces de performance e identificar gargalos!
 */
app.get('/api/slow', async (req, res) => {
  console.log('🐌 Iniciando operação lenta...');
  
  // Simula delay de 1-3 segundos (tipo de query complexa)
  const delay = 1000 + Math.random() * 2000;
  
  await new Promise(resolve => setTimeout(resolve, delay));
  
  console.log(`✅ Operação lenta concluída em ${delay.toFixed(0)}ms`);
  
  res.json({
    message: 'Operação lenta concluída',
    duration: `${delay.toFixed(0)}ms`,
  });
});

/**
 * 🔗 REDIRECT DE EXEMPLO
 * 
 * Mostra traces com múltiplos spans (redirects)
 */
app.get('/api/redirect-demo', (req, res) => {
  res.redirect('/api/health');
});

// ============================================================================
// MIDDLEWARE DE ERRO
// ============================================================================

app.use((err, req, res, next) => {
  console.error('❌ Erro capturado:', err);
  res.status(500).json({
    error: 'Erro interno do servidor',
    message: err.message,
  });
});

// ============================================================================
// INICIALIZAÇÃO DO SERVIDOR
// ============================================================================

const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
  console.log('\n🚀 Servidor iniciado!');
  console.log(`📡 Servidor rodando em: http://localhost:${PORT}`);
  console.log('\n📋 Endpoints disponíveis:');
  console.log('   GET  /api/health              - Health check');
  console.log('   GET  /api/users               - Lista usuários');
  console.log('   GET  /api/users/:id           - Busca usuário');
  console.log('   POST /api/users               - Cria usuário');
  console.log('   GET  /api/products            - Lista produtos (20% erro)');
  console.log('   GET  /api/slow                - Operação lenta');
  console.log('   GET  /api/redirect-demo       - Redirect exemplo');
  console.log('\n💡 Dica: Agora acesse http://localhost:8080 para ver os dados no SigNoz!\n');
});

// ============================================================================
// SHUTDOWN GRACEFUL
// ============================================================================

process.on('SIGTERM', () => {
  console.log('\n🛑 Recebido SIGTERM, encerrando servidor graciosamente...');
  process.exit(0);
});

/**
 * 📚 CONCEITOS DE OBSERVABILIDADE DEMONSTRADOS:
 * 
 * 1. ✅ Traces automáticos de todas as requisições HTTP
 * 2. ✅ Spans para cada operação (DB, delays, etc)
 * 3. ✅ Rastreamento de erros (status 404, 500, etc)
 * 4. ✅ Métricas de performance (latência, throughput)
 * 5. ✅ Contexto HTTP propagado automaticamente
 * 6. ✅ Logs estruturados
 * 
 * 🎯 TUDO ISSO SEM MODIFICAR MANUALMENTE CADA ENDPOINT!
 * O OpenTelemetry faz a mágica automaticamente! ✨
 */


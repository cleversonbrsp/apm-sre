/**
 *  SAMPLE NODE.JS + EXPRESS APPLICATION
 *
 * This API demonstrates:
 * - REST endpoints
 * - A simulated database
 * - Different request patterns
 * - Endpoints tailor-made to highlight observability signals
 */

const express = require('express');
const app = express();

// JSON body parsing
app.use(express.json());

/**
 *  NOTE: Instrumentation is loaded before this file runs.
 * Command: node -r ./instrumentation.js server.js
 *
 * That means every HTTP request is already traced automatically!
 */

// Mock database state
let users = [
  { id: 1, name: 'Alice Smith', email: 'alice@example.com', role: 'admin' },
  { id: 2, name: 'Bob Johnson', email: 'bob@example.com', role: 'user' },
  { id: 3, name: 'Carol Davis', email: 'carol@example.com', role: 'user' },
];

let products = [
  { id: 1, name: 'Laptop', price: 2999.99, stock: 15 },
  { id: 2, name: 'Wireless Mouse', price: 89.9, stock: 50 },
  { id: 3, name: 'Mechanical Keyboard', price: 199.9, stock: 30 },
];

// ============================================================================
// API ROUTES
// ============================================================================

/**
 *  ROOT ENDPOINT
 *
 * Returns a quick overview of the API
 */
app.get('/', (req, res) => {
  res.json({
    message: ' Node.js API instrumented with OpenTelemetry',
    version: '1.0.0',
    endpoints: {
      health: 'GET /api/health',
      users: {
        list: 'GET /api/users',
        get: 'GET /api/users/:id',
        create: 'POST /api/users',
      },
      products: 'GET /api/products (20% chance of failure)',
      slow: 'GET /api/slow (simulated slow operation)',
      redirect: 'GET /api/redirect-demo',
    },
    signoz: 'http://localhost:8080',
    instrumentation: 'Auto-instrumented OpenTelemetry SDK',
  });
});

/**
 *  HEALTH CHECK
 *
 * Basic endpoint to confirm the service is alive.
 * Automatically traced by OpenTelemetry!
 */
app.get('/api/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
  });
});

/**
 *  LIST USERS
 *
 * Returns every user in the mock database.
 * Great for observing successful traces.
 */
app.get('/api/users', (req, res) => {
  console.log(' Listing all users');

  // Simulate a database latency
  setTimeout(() => {
    res.json({
      count: users.length,
      users,
    });
  }, 100);
});

/**
 *  GET USER BY ID
 *
 * Returns a single user and showcases custom attributes.
 */
app.get('/api/users/:id', (req, res) => {
  const id = parseInt(req.params.id, 10);
  const user = users.find(u => u.id === id);

  console.log(` Fetching user ID: ${id}`);

  if (!user) {
    return res.status(404).json({
      error: 'User not found',
      requestedId: id,
    });
  }

  res.json(user);
});

/**
 *  CREATE USER
 *
 * Adds a new user and illustrates write operations.
 */
app.post('/api/users', (req, res) => {
  const { name, email, role } = req.body;

  console.log(` Creating user: ${name} (${email})`);

  if (!name || !email) {
    return res.status(400).json({
      error: 'Name and email are required',
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
    message: 'User created successfully',
    user: newUser,
  });
});

/**
 *  LIST PRODUCTS (WITH FAILURES)
 *
 * Randomly fails to demonstrate error tracing.
 */
app.get('/api/products', (req, res) => {
  console.log(' Listing products…');

  // 20% failure rate to demonstrate errors
  if (Math.random() < 0.2) {
    console.error(' Failed to fetch products from the database');
    return res.status(500).json({
      error: 'Internal error fetching products',
      message: 'Database connection failed',
    });
  }

  res.json({
    count: products.length,
    products,
  });
});

/**
 *  SLOW ENDPOINT
 *
 * Simulates a slow operation (e.g., complex query or third-party call)
 * Perfect to observe latency in traces.
 */
app.get('/api/slow', async (req, res) => {
  console.log(' Starting slow operation…');

  // Simulate a 1–3 second delay
  const delay = 1000 + Math.random() * 2000;
  await new Promise(resolve => setTimeout(resolve, delay));

  console.log(` Slow operation completed in ${delay.toFixed(0)}ms`);

  res.json({
    message: 'Slow operation completed',
    duration: `${delay.toFixed(0)}ms`,
  });
});

/**
 *  REDIRECT EXAMPLE
 *
 * Produces multiple spans to illustrate redirects.
 */
app.get('/api/redirect-demo', (req, res) => {
  res.redirect('/api/health');
});

// ============================================================================
// ERROR HANDLER
// ============================================================================

app.use((err, req, res, next) => {
  console.error(' Unhandled error:', err);
  res.status(500).json({
    error: 'Internal server error',
    message: err.message,
  });
});

// ============================================================================
// SERVER STARTUP
// ============================================================================

const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
  console.log('\n Server started!');
  console.log(` Listening at: http://localhost:${PORT}`);
  console.log('\n Available endpoints:');
  console.log('   GET  /api/health              - Health check');
  console.log('   GET  /api/users               - List users');
  console.log('   GET  /api/users/:id           - Get user by ID');
  console.log('   POST /api/users               - Create user');
  console.log('   GET  /api/products            - List products (20% error rate)');
  console.log('   GET  /api/slow                - Simulated slow call');
  console.log('   GET  /api/redirect-demo       - Redirect example');
  console.log('\n Tip: Head over to http://localhost:8080 to explore SigNoz dashboards!\n');
});

// ============================================================================
// GRACEFUL SHUTDOWN
// ============================================================================

process.on('SIGTERM', () => {
  console.log('\n Received SIGTERM, shutting down gracefully...');
  process.exit(0);
});

/**
 *  OBSERVABILITY CONCEPTS DEMONSTRATED
 *
 * 1. Automatic traces for every HTTP request
 * 2. Spans for application work (DB delays, slow ops, etc.)
 * 3. Error tracking (404, 500, random failures)
 * 4. Latency & throughput visibility
 * 5. Automatic HTTP context propagation
 * 6. Structured logs
 *
 *  All of this with zero manual tracing code inside each endpoint—OpenTelemetry does the heavy lifting!
 */


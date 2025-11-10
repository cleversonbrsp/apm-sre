# 🚀 Quick Start Guide

## ✅ You already have a working app!

Your Node.js application is already set up and running!

### Current Setup:
- **Location**: `labs/example-application/app-nodejs/`
- **Status**: Dependencies already installed ✅
- **App Running**: Check if port 3000 is in use
- **SigNoz**: Running on http://localhost:8080 ✅

### To Start the Application:

```bash
cd labs/example-application/app-nodejs
npm start
```

### To Test the Application:

Open a new terminal and run:

```bash
# Health check
curl http://localhost:3000/api/health

# List users
curl http://localhost:3000/api/users

# Create a user
curl -X POST http://localhost:3000/api/users \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com"}'

# Try the slow endpoint
curl http://localhost:3000/api/slow

# Products (has 20% chance of error)
curl http://localhost:3000/api/products
```

### View Data in SigNoz:

1. Open http://localhost:8080
2. Go to **Traces** to see all your requests
3. Go to **Services** to see service map
4. Explore **Metrics** for performance data

### Why the error occurred:

You were in the wrong directory! The `package.json` is inside `app-nodejs/` subdirectory.

**Wrong**: `labs/example-application/` ❌
**Right**: `labs/example-application/app-nodejs/` ✅

### Need Help?

Check:
- `COMO_USAR.md` – Detailed usage guide
- `app-nodejs/README.md` – Application documentation
- `GUIA_INSTRUMENTACAO_DETALHADO.md` – Instrumentation details

Happy monitoring! 📊

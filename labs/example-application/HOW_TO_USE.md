# 🚀 How to Use the Sample Applications

This hands-on guide walks you step-by-step through running and testing the sample applications.

## 📋 Prerequisites

✅ SigNoz running via Docker:
```bash
cd /home/cleverson/Documents/signoz-lab/signoz/deploy/docker
docker-compose up -d
```

✅ Confirm everything is up:
```bash
docker ps
```

You should see:
- `signoz` – SigNoz frontend
- `signoz-clickhouse` – Database
- `signoz-otel-collector` – OpenTelemetry Collector
- `signoz-zookeeper-1` – ZooKeeper

---

## 🟢 Option 1: Node.js Application

### Step 1: Navigate to the App

```bash
cd /github/crs-repos/apm-sre/labs/example-application/app-nodejs
```

### Step 2: Install Dependencies

```bash
npm install
```

This installs:
- Express (web framework)
- OpenTelemetry SDK
- Auto instrumentations
- OTLP exporter

### Step 3: Run the Application

```bash
npm start
```

You should see:

```
⚡ OpenTelemetry SDK initialized
📊 Sending traces and metrics to: http://localhost:4317
🔍 Data will appear in SigNoz at: http://localhost:8080

🚀 Server started!
📡 Server running at: http://localhost:3000
```

### Step 4: Generate Traffic

Open a **second terminal** and run:

```bash
# Health check
curl http://localhost:3000/api/health

# List users
curl http://localhost:3000/api/users

# Create a user
curl -X POST http://localhost:3000/api/users \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com"}'

# Slow endpoint
curl http://localhost:3000/api/slow
```

### Step 5: View Data in SigNoz

1. Go to http://localhost:8080
2. Sign in if required
3. Explore:
   - **Traces**: Click “Traces” in the sidebar
   - **Services**: Inspect your services
   - **Metrics**: Review performance dashboards

---

## 🐍 Option 2: Python Application

### Step 1: Navigate to the App

```bash
cd /home/cleverson/Documents/signoz-lab/example-application/app-python
```

### Step 2: Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- Flask (web framework)
- OpenTelemetry Python SDK
- Auto instrumentations
- OTLP exporter

### Step 4: Run the Application

```bash
python app.py
```

You should see:

```
⚡ OpenTelemetry SDK initialized
📊 Sending traces and metrics to: http://localhost:4317
🔍 Data will appear in SigNoz at: http://localhost:8080

🚀 Server started!
📡 Server running at: http://localhost:5000
```

### Step 5: Generate Traffic

Open a **second terminal** and run:

```bash
# Health check
curl http://localhost:5000/api/health

# List users
curl http://localhost:5000/api/users

# Create a user
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com"}'

# Endpoint with random errors
curl http://localhost:5000/api/random-error
```

### Step 6: View Data in SigNoz

1. Open http://localhost:8080
2. Explore the telemetry produced by the Python app

---

## 🎯 Recommended Activities

### 1. Explore Traces

In the SigNoz UI:

1. Navigate to **Traces**
2. Review the list of HTTP requests
3. Click a trace to inspect:
   - All spans
   - Duration of each operation
   - Attributes
   - Logs

**Exercise:** Compare traces for fast vs. slow endpoints!

### 2. Review the Service Map

1. Open **Service Map**
2. Visualize your application architecture
3. Inspect dependencies and data flow

**Exercise:** Trigger a variety of requests and watch the map evolve!

### 3. Analyze Metrics

1. Go to **Metrics**
2. Explore:
   - **Latency**: Response times
   - **Error Rate**: Failure percentage
   - **Throughput**: Requests per second

**Exercise:** Generate a quick burst of requests:
```bash
for i in {1..100}; do curl -s http://localhost:3000/api/health > /dev/null; done
```

### 4. View Logs (if configured)

1. Open **Logs**
2. Watch logs in real time
3. Filter by service, error, etc.

**Exercise:** Call the error endpoint:
```bash
curl http://localhost:3000/api/products  # May produce an error
```

### 5. Build a Dashboard

1. Navigate to **Dashboards**
2. Click **New Dashboard**
3. Add panels for:
   - Latency metrics
   - Error rate
   - Throughput

**Exercise:** Build a dashboard tailored to your sample app!

---

## 🔍 What to Look For in SigNoz

### Successful Traces

- **Span**: Express/Flask request
- **Status**: 200 OK
- **Duration**: Total execution time
- **Attributes**: Method, Route, Status Code

### Error Traces

- **Span**: Request with failure
- **Status**: 4xx or 5xx
- **Error**: true
- **Error Message**: Description of the failure

### Slow Endpoints

- **Duration**: > 1s
- **Spans**: Multiple operations
- **Bottlenecks**: Identify where time is spent

### Service Map

- **Services**: `signoz-example-nodejs` or `signoz-example-python`
- **Connections**: Data flow between services
- **Health**: Service status indicators

---

## 🐛 Troubleshooting

### “I can’t see data in SigNoz”

**Check:**

1. ✅ SigNoz is running:
   ```bash
   docker ps | grep signoz
   ```

2. ✅ OTel Collector is running:
   ```bash
   docker ps | grep otel-collector
   ```

3. ✅ The app is sending data:
   - Console shows no errors?
   - Logs mention “OpenTelemetry SDK initialized”?

4. ✅ Ports are correct:
   - Node.js: 3000
   - Python: 5000
   - OTel Collector: 4317

**Fix:**

```bash
# Check collector logs
docker logs signoz-otel-collector

# Restart everything
cd /home/cleverson/Documents/signoz-lab/signoz/deploy/docker
docker-compose restart
```

### “Dependency installation failed”

**Node.js:**
```bash
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

**Python:**
```bash
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### “Port already in use”

**Option 1:** Kill the process on that port:
```bash
# Linux
sudo lsof -ti:3000 | xargs kill -9
# or
sudo fuser -k 3000/tcp

# Inspect listening ports
netstat -tulpn | grep LISTEN
```

**Option 2:** Change the port:
```javascript
// Node.js: server.js
const PORT = process.env.PORT || 3001;  // Changed from 3000 to 3001
```

```python
# Python: app.py
app.run(host='0.0.0.0', port=5001, debug=True)  # Changed from 5000 to 5001
```

---

## 🎓 Next Steps

Now that you can instrument applications, try:

1. ✅ **Instrumenting your own service**
   - Copy `instrumentation.js` or `instrumentation.py`
   - Adapt it to your stack
   - Deploy and monitor!

2. ✅ **Setting up alerts**
   - In SigNoz: Settings → Alerts
   - Configure notifications for errors

3. ✅ **Integrating with CI/CD**
   - Add observability checks to pipelines
   - Automate deploys with monitoring

4. ✅ **Adding custom instrumentation**
   - Spans for critical operations
   - Custom metrics
   - Business attributes

---

## 📚 Resources

- [SigNoz Documentation](https://signoz.io/docs/)
- [OpenTelemetry](https://opentelemetry.io/)
- [Node.js Instrumentation](https://signoz.io/docs/instrumentation/nodejs/)
- [Python Instrumentation](https://signoz.io/docs/instrumentation/python/)

---

## ✨ Tips

💡 **Tip 1:** Run both Node.js and Python apps simultaneously and compare!  

💡 **Tip 2:** Use load testing to generate more data:
```bash
# Install Apache Bench
sudo apt-get install apache2-utils  # Linux
brew install httpd                   # Mac

# Generate load
ab -n 1000 -c 10 http://localhost:3000/api/health
```

💡 **Tip 3:** Try different scenarios:
- Normal requests
- Slow requests
- Error scenarios
- High RPS bursts

Enjoy exploring observability! 🚀


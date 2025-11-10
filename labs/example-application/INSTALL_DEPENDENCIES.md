# 📦 Dependency Installation

This guide walks you through installing every dependency required to run the sample applications.

---

## 🟢 Node.js – Full Setup

### 1. Install Node.js (if you don’t have it)

**Ubuntu/Debian:**
```bash
# Using apt
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation
node --version  # Should print v18.x or newer
npm --version   # Should print 9.x or newer
```

**macOS:**
```bash
# Using Homebrew
brew install node

# Verify installation
node --version
npm --version
```

**Windows:**
1. Download the installer at https://nodejs.org/
2. Run the installer
3. Confirm in the terminal:
```cmd
node --version
npm --version
```

### 2. Install Application Dependencies

```bash
cd /home/cleverson/Documents/signoz-lab/example-application/app-nodejs

# Install all dependencies
npm install
```

**This installs:**
- express@^4.18.2 – Web framework
- @opentelemetry/sdk-node@^0.47.0 – Node.js SDK
- @opentelemetry/auto-instrumentations-node@^0.41.0 – Auto instrumentation
- @opentelemetry/exporter-otlp-grpc@^0.47.0 – OTLP exporter
- And their dependencies

**Estimated time:** 2–5 minutes

### 3. Verify Installation

```bash
# List installed packages
npm list --depth=0

# Make sure OpenTelemetry is available
node -e "require('@opentelemetry/sdk-node'); console.log('✅ OpenTelemetry OK')"
```

---

## 🐍 Python – Full Setup

### 1. Install Python 3.8+ (if you don’t have it)

**Ubuntu/Debian:**
```bash
# Python 3 ships by default in most cases
python3 --version  # Should print 3.8 or newer

# If not, install:
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv

# Verify installation
python3 --version
pip3 --version
```

**macOS:**
```bash
# Python 3 ships by default
python3 --version

# If you need a newer version:
brew install python3

# Verify installation
python3 --version
pip3 --version
```

**Windows:**
1. Download Python from https://www.python.org/downloads/
2. During installation, **check “Add Python to PATH”**
3. Confirm in the terminal:
```cmd
python --version
pip --version
```

### 2. Create a Virtual Environment

**Linux/macOS:**
```bash
cd /home/cleverson/Documents/signoz-lab/example-application/app-python

# Create the virtual environment
python3 -m venv venv

# Activate the venv
source venv/bin/activate

# You should see (venv) at the beginning of the prompt
```

**Windows:**
```cmd
cd C:\Users\YourUser\Documents\signoz-lab\example-application\app-python

# Create the virtual environment
python -m venv venv

# Activate the venv
venv\Scripts\activate

# You should see (venv) at the beginning of the prompt
```

### 3. Upgrade pip

```bash
# Upgrade pip to the latest version
pip install --upgrade pip
```

### 4. Install Dependencies

```bash
# Install everything from requirements.txt
pip install -r requirements.txt
```

**This installs:**
- Flask==3.0.0 – Web framework
- opentelemetry-api==1.21.0 – OpenTelemetry API
- opentelemetry-sdk==1.21.0 – Python SDK
- opentelemetry-exporter-otlp-proto-grpc==1.21.0 – OTLP exporter
- opentelemetry-instrumentation-flask==0.42b0 – Flask auto instrumentation
- opentelemetry-instrumentation-requests==0.42b0 – HTTP auto instrumentation
- And their dependencies

**Estimated time:** 3–5 minutes

### 5. Verify Installation

```bash
# List installed packages
pip list

# Make sure OpenTelemetry is available
python -c "import opentelemetry; print('✅ OpenTelemetry OK')"
```

---

## 🐳 Docker – Verification

### 1. Check Docker

```bash
docker --version
docker-compose --version
```

### 2. Check SigNoz

```bash
cd /home/cleverson/Documents/signoz-lab/signoz/deploy/docker

# Check current status
docker-compose ps

# If it’s not running, start it:
docker-compose up -d

# Tail the logs
docker-compose logs -f
```

### 3. Check Ports

The following ports must be available:
- **3000**: Node.js (or whichever you choose)
- **5000**: Python (or whichever you choose)
- **8080**: SigNoz UI
- **4317**: OTel Collector (gRPC)
- **4318**: OTel Collector (HTTP)

**Check ports in use:**
```bash
# Linux
sudo netstat -tulpn | grep LISTEN

# macOS
lsof -i -P | grep LISTEN
```

---

## 🧪 Validate the Full Setup

### Node.js Test

```bash
cd /home/cleverson/Documents/signoz-lab/example-application/app-nodejs

# Start the application
npm start

# In another terminal, hit an endpoint:
curl http://localhost:3000/api/health

# Expected response:
# {"status":"healthy","timestamp":"...","uptime":0.xxx}
```

### Python Test

```bash
cd /home/cleverson/Documents/signoz-lab/example-application/app-python

# Activate the venv
source venv/bin/activate

# Start the application
python app.py

# In another terminal, hit an endpoint:
curl http://localhost:5000/api/health

# Expected response:
# {"status":"healthy","service":"signoz-example-python",...}
```

### SigNoz Test

```bash
# Check the UI
curl -I http://localhost:8080

# Expected: HTTP 200 OK
```

---

## 🐛 Troubleshooting

### Node.js

**Error: “Cannot find module”**
```bash
cd app-nodejs
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

**Error: “Port 3000 already in use”**
```bash
# Find the process on port 3000
sudo lsof -ti:3000

# Kill the process
sudo lsof -ti:3000 | xargs kill -9

# Or pick another port
PORT=3001 npm start
```

### Python

**Error: “virtualenv not found”**
```bash
sudo apt-get install python3-venv  # Ubuntu/Debian
# or
brew install python3-venv          # macOS
```

**Error: “pip not found”**
```bash
# Reinstall pip
python3 -m ensurepip --upgrade

# Or use pip3
pip3 install -r requirements.txt
```

**Error: “Permission denied” when installing**
```bash
# NEVER use sudo with a venv!
# Always activate the virtual environment:
source venv/bin/activate
pip install -r requirements.txt
```

**Forgot to activate the venv?**
```bash
# You’ll hit errors when running; remember:
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

### Docker

**Error: “Cannot connect to Docker daemon”**
```bash
# Check if Docker is running
sudo systemctl status docker

# Start Docker
sudo systemctl start docker

# Add your user to the docker group
sudo usermod -aG docker $USER

# Log out and log back in
```

**Error: “Port already allocated”**
```bash
# See which process is using the port
sudo lsof -i :8080

# Stop containers
cd signoz/deploy/docker
docker-compose down

# Remove stale containers
docker-compose down -v

# Start again
docker-compose up -d
```

**Error: “Out of memory”**
```bash
# Check memory usage
docker stats

# Clean unused resources
docker system prune -a

# Increase memory (Docker Desktop settings)
```

---

## ✅ Final Checklist

Before moving on, confirm that:

- [ ] Node.js 14+ is installed
- [ ] npm is installed
- [ ] Python 3.8+ is installed
- [ ] pip is installed
- [ ] Docker is installed and running
- [ ] Docker Compose is installed
- [ ] SigNoz is running via docker-compose
- [ ] Ports are free (3000, 5000, 8080, 4317)
- [ ] Node.js dependencies are installed
- [ ] Python virtual environment is created
- [ ] Python dependencies are installed
- [ ] All applications were tested

---

## 📚 Next Steps

With every dependency ready:

1. ✅ Read `COMO_USAR.md` (How to Use)  
2. ✅ Follow the `README.md` for your chosen application  
3. ✅ Explore the SigNoz UI at http://localhost:8080  
4. ✅ Have fun instrumenting your own services!

---

## 🆘 Need Help?

- 📖 Documentation: [signoz.io/docs](https://signoz.io/docs/)
- 💬 Discord: [Signoz Discord](https://discord.com/invite/signoz)
- 🐛 GitHub Issues: [github.com/SigNoz/signoz](https://github.com/SigNoz/signoz)


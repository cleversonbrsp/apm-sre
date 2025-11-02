# 📦 Instalação de Dependências

Este guia te ajuda a instalar todas as dependências necessárias para executar as aplicações de exemplo.

---

## 🟢 Node.js - Instalação Completa

### 1. Instalar Node.js (se não tiver)

**Ubuntu/Debian:**
```bash
# Usando apt
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verificar instalação
node --version  # Deve mostrar v18.x ou superior
npm --version   # Deve mostrar 9.x ou superior
```

**macOS:**
```bash
# Usando Homebrew
brew install node

# Verificar instalação
node --version
npm --version
```

**Windows:**
1. Baixe o instalador em: https://nodejs.org/
2. Execute o instalador
3. Verifique no terminal:
```cmd
node --version
npm --version
```

### 2. Instalar Dependências da Aplicação

```bash
cd /home/cleverson/Documents/signoz-lab/aplicacao-exemplo/app-nodejs

# Instalar todas as dependências
npm install
```

**Isso instalará:**
- express@^4.18.2 - Framework web
- @opentelemetry/sdk-node@^0.47.0 - SDK Node.js
- @opentelemetry/auto-instrumentations-node@^0.41.0 - Auto-instrumentação
- @opentelemetry/exporter-otlp-grpc@^0.47.0 - Exportador
- E suas dependências

**Tempo estimado**: 2-5 minutos

### 3. Verificar Instalação

```bash
# Verificar pacotes instalados
npm list --depth=0

# Testar se o OpenTelemetry está disponível
node -e "require('@opentelemetry/sdk-node'); console.log('✅ OpenTelemetry OK')"
```

---

## 🐍 Python - Instalação Completa

### 1. Instalar Python 3.8+ (se não tiver)

**Ubuntu/Debian:**
```bash
# Python 3 já vem instalado na maioria dos casos
python3 --version  # Deve mostrar 3.8 ou superior

# Se não tiver, instale:
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv

# Verificar instalação
python3 --version
pip3 --version
```

**macOS:**
```bash
# Python 3 já vem instalado
python3 --version

# Se precisar atualizar:
brew install python3

# Verificar instalação
python3 --version
pip3 --version
```

**Windows:**
1. Baixe Python de: https://www.python.org/downloads/
2. Durante instalação, **marque "Add Python to PATH"**
3. Verifique no terminal:
```cmd
python --version
pip --version
```

### 2. Criar Ambiente Virtual

**Linux/macOS:**
```bash
cd /home/cleverson/Documents/signoz-lab/aplicacao-exemplo/app-python

# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate

# Você verá (venv) no início da linha do terminal
```

**Windows:**
```cmd
cd C:\Users\SeuUsuario\Documents\signoz-lab\aplicacao-exemplo\app-python

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
venv\Scripts\activate

# Você verá (venv) no início da linha do terminal
```

### 3. Atualizar pip

```bash
# Atualizar pip para versão mais recente
pip install --upgrade pip
```

### 4. Instalar Dependências

```bash
# Instalar todas as dependências do requirements.txt
pip install -r requirements.txt
```

**Isso instalará:**
- Flask==3.0.0 - Framework web
- opentelemetry-api==1.21.0 - API OpenTelemetry
- opentelemetry-sdk==1.21.0 - SDK Python
- opentelemetry-exporter-otlp-proto-grpc==1.21.0 - Exportador
- opentelemetry-instrumentation-flask==0.42b0 - Auto-instrumentação Flask
- opentelemetry-instrumentation-requests==0.42b0 - Auto-instrumentação HTTP
- E suas dependências

**Tempo estimado**: 3-5 minutos

### 5. Verificar Instalação

```bash
# Verificar pacotes instalados
pip list

# Testar se o OpenTelemetry está disponível
python -c "import opentelemetry; print('✅ OpenTelemetry OK')"
```

---

## 🐳 Docker - Verificação

### 1. Verificar Docker

```bash
docker --version
docker-compose --version
```

### 2. Verificar SigNoz

```bash
cd /home/cleverson/Documents/signoz-lab/signoz/deploy/docker

# Ver se está rodando
docker-compose ps

# Se não estiver rodando, inicie:
docker-compose up -d

# Verificar logs
docker-compose logs -f
```

### 3. Verificar Portas

As seguintes portas devem estar livres:
- **3000**: Node.js (ou outra que você escolher)
- **5000**: Python (ou outra que você escolher)
- **8080**: SigNoz UI
- **4317**: Otel Collector (gRPC)
- **4318**: Otel Collector (HTTP)

**Verificar portas em uso:**
```bash
# Linux
sudo netstat -tulpn | grep LISTEN

# macOS
lsof -i -P | grep LISTEN
```

---

## 🧪 Testar Instalação Completa

### Teste Node.js

```bash
cd /home/cleverson/Documents/signoz-lab/aplicacao-exemplo/app-nodejs

# Executar aplicação
npm start

# Em outro terminal, testar:
curl http://localhost:3000/api/health

# Deve retornar:
# {"status":"healthy","timestamp":"...","uptime":0.xxx}
```

### Teste Python

```bash
cd /home/cleverson/Documents/signoz-lab/aplicacao-exemplo/app-python

# Ativar venv
source venv/bin/activate

# Executar aplicação
python app.py

# Em outro terminal, testar:
curl http://localhost:5000/api/health

# Deve retornar:
# {"status":"healthy","service":"signoz-example-python",...}
```

### Teste SigNoz

```bash
# Verificar UI
curl -I http://localhost:8080

# Deve retornar HTTP 200 OK
```

---

## 🐛 Solução de Problemas

### Node.js

**Erro: "Cannot find module"**
```bash
cd app-nodejs
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

**Erro: "Port 3000 already in use"**
```bash
# Encontrar processo na porta 3000
sudo lsof -ti:3000

# Matar processo
sudo lsof -ti:3000 | xargs kill -9

# Ou usar outra porta
PORT=3001 npm start
```

### Python

**Erro: "virtualenv not found"**
```bash
sudo apt-get install python3-venv  # Ubuntu/Debian
# ou
brew install python3-venv  # macOS
```

**Erro: "pip not found"**
```bash
# Reinstalar pip
python3 -m ensurepip --upgrade

# Ou usar pip3
pip3 install -r requirements.txt
```

**Erro: "Permission denied" ao instalar**
```bash
# NUNCA use sudo com venv!
# Use sempre o ambiente virtual:
source venv/bin/activate
pip install -r requirements.txt
```

**Esqueceu de ativar o venv?**
```bash
# Você verá erro ao executar, lembre-se:
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

### Docker

**Erro: "Cannot connect to Docker daemon"**
```bash
# Verificar se Docker está rodando
sudo systemctl status docker

# Iniciar Docker
sudo systemctl start docker

# Adicionar seu usuário ao grupo docker
sudo usermod -aG docker $USER

# Fazer logout e login novamente
```

**Erro: "Port already allocated"**
```bash
# Ver porta em uso
sudo lsof -i :8080

# Parar containers
cd signoz/deploy/docker
docker-compose down

# Remover containers antigos
docker-compose down -v

# Iniciar novamente
docker-compose up -d
```

**Erro: "Out of memory"**
```bash
# Ver uso de memória
docker stats

# Limpar recursos não utilizados
docker system prune -a

# Aumentar memória do Docker (Docker Desktop Settings)
```

---

## ✅ Checklist Final

Antes de começar, certifique-se de que:

- [ ] Node.js 14+ instalado
- [ ] npm instalado
- [ ] Python 3.8+ instalado
- [ ] pip instalado
- [ ] Docker instalado e rodando
- [ ] Docker Compose instalado
- [ ] SigNoz rodando via docker-compose
- [ ] Portas livres (3000, 5000, 8080, 4317)
- [ ] Dependências Node.js instaladas
- [ ] Ambiente virtual Python criado
- [ ] Dependências Python instaladas
- [ ] Todas as aplicações testadas

---

## 📚 Próximos Passos

Agora que todas as dependências estão instaladas:

1. ✅ Leia: `COMO_USAR.md`
2. ✅ Execute: `README.md` da sua aplicação escolhida
3. ✅ Explore: SigNoz UI em http://localhost:8080
4. ✅ Divirta-se: Instrumentando suas próprias aplicações!

---

## 🆘 Precisa de Ajuda?

- 📖 Documentação: [signoz.io/docs](https://signoz.io/docs/)
- 💬 Discord: [Signoz Discord](https://discord.com/invite/signoz)
- 🐛 GitHub Issues: [github.com/SigNoz/signoz](https://github.com/SigNoz/signoz)


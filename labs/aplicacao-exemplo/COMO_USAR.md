# 🚀 Como Usar as Aplicações de Exemplo

Este guia prático te ensina passo a passo como executar e testar as aplicações de exemplo.

## 📋 Pré-requisitos

✅ SigNoz rodando via Docker:
```bash
cd /home/cleverson/Documents/signoz-lab/signoz/deploy/docker
docker-compose up -d
```

✅ Verifique se está tudo rodando:
```bash
docker ps
```

Você deve ver:
- `signoz` - Aplicação principal
- `signoz-clickhouse` - Banco de dados
- `signoz-otel-collector` - Coletor OpenTelemetry
- `signoz-zookeeper-1` - ZooKeeper

---

## 🟢 Opção 1: Aplicação Node.js

### Passo 1: Navegar para a Aplicação

```bash
cd /home/cleverson/Documents/signoz-lab/aplicacao-exemplo/app-nodejs
```

### Passo 2: Instalar Dependências

```bash
npm install
```

Isso instalará:
- Express (framework web)
- OpenTelemetry SDK
- Auto-instrumentações
- Exportador OTLP

### Passo 3: Executar a Aplicação

```bash
npm start
```

Você verá:

```
⚡ OpenTelemetry SDK inicializado
📊 Enviando traces e métricas para: http://localhost:4317
🔍 Dados aparecerão no SigNoz em: http://localhost:8080

🚀 Servidor iniciado!
📡 Servidor rodando em: http://localhost:3000
```

### Passo 4: Gerar Tráfego

Abra um **segundo terminal** e execute:

```bash
# Health check
curl http://localhost:3000/api/health

# Listar usuários
curl http://localhost:3000/api/users

# Criar usuário
curl -X POST http://localhost:3000/api/users \
  -H "Content-Type: application/json" \
  -d '{"name":"Teste User","email":"teste@example.com"}'

# Endpoint lento
curl http://localhost:3000/api/slow
```

### Passo 5: Ver Dados no SigNoz

1. Acesse: http://localhost:8080
2. Faça login (se necessário)
3. Explore:
   - **Traces**: Clique em "Traces" no menu lateral
   - **Services**: Veja seus serviços
   - **Metrics**: Métricas de performance

---

## 🐍 Opção 2: Aplicação Python

### Passo 1: Navegar para a Aplicação

```bash
cd /home/cleverson/Documents/signoz-lab/aplicacao-exemplo/app-python
```

### Passo 2: Criar Ambiente Virtual

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
```

### Passo 3: Instalar Dependências

```bash
pip install -r requirements.txt
```

Isso instalará:
- Flask (framework web)
- OpenTelemetry SDK para Python
- Auto-instrumentações
- Exportador OTLP

### Passo 4: Executar a Aplicação

```bash
python app.py
```

Você verá:

```
⚡ OpenTelemetry SDK inicializado
📊 Enviando traces e métricas para: http://localhost:4317
🔍 Dados aparecerão no SigNoz em: http://localhost:8080

🚀 Servidor iniciado!
📡 Servidor rodando em: http://localhost:5000
```

### Passo 5: Gerar Tráfego

Abra um **segundo terminal** e execute:

```bash
# Health check
curl http://localhost:5000/api/health

# Listar usuários
curl http://localhost:5000/api/users

# Criar usuário
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -d '{"name":"Teste User","email":"teste@example.com"}'

# Endpoint com erro aleatório
curl http://localhost:5000/api/random-error
```

### Passo 6: Ver Dados no SigNoz

1. Acesse: http://localhost:8080
2. Explore os dados gerados pela aplicação Python

---

## 🎯 Atividades Recomendadas

### 1. Explorar Traces

No SigNoz UI:

1. Vá para **Traces**
2. Você verá todas as requisições HTTP
3. Clique em um trace para ver:
   - Todos os spans
   - Duração de cada operação
   - Atributos
   - Logs

**Exercício**: Compare traces de endpoints rápidos vs lentos!

### 2. Ver Service Map

1. Vá para **Service Map**
2. Visualize a arquitetura da sua aplicação
3. Veja dependências e fluxo de dados

**Exercício**: Execute múltiplos tipos de requests e observe o mapa!

### 3. Analisar Métricas

1. Vá para **Metrics**
2. Explore:
   - **Latency**: Tempo de resposta
   - **Error Rate**: Taxa de erros
   - **Throughput**: Requisições por segundo

**Exercício**: Gere muitos requests rapidamente:
```bash
for i in {1..100}; do curl -s http://localhost:3000/api/health > /dev/null; done
```

### 4. Ver Logs (se configurado)

1. Vá para **Logs**
2. Veja logs em tempo real
3. Filtre por serviço, erro, etc.

**Exercício**: Execute o endpoint que gera erro:
```bash
curl http://localhost:3000/api/products  # Pode gerar erro
```

### 5. Criar Dashboard

1. Vá para **Dashboards**
2. Clique em **New Dashboard**
3. Adicione painéis com:
   - Métricas de latência
   - Taxa de erro
   - Throughput

**Exercício**: Crie um dashboard para sua aplicação de exemplo!

---

## 🔍 O Que Procurar no SigNoz

### Traces Bem-Sucedidos

- **Span**: Express/Fask request
- **Status**: 200 OK
- **Duration**: Tempo total
- **Attributes**: Method, Route, Status Code

### Traces com Erro

- **Span**: Request com erro
- **Status**: 4xx ou 5xx
- **Error**: true
- **Error Message**: Mensagem de erro

### Endpoints Lentos

- **Duration**: > 1s
- **Spans**: Múltiplas operações
- **Bottlenecks**: Onde está o tempo?

### Service Map

- **Services**: signoz-example-nodejs ou signoz-example-python
- **Connections**: Fluxo de dados
- **Health**: Status dos serviços

---

## 🐛 Troubleshooting

### "Não vejo dados no SigNoz"

**Verifique:**

1. ✅ SigNoz está rodando?
   ```bash
   docker ps | grep signoz
   ```

2. ✅ Otel Collector está rodando?
   ```bash
   docker ps | grep otel-collector
   ```

3. ✅ Aplicação está enviando dados?
   - Console não mostra erros?
   - Logs mostram "OpenTelemetry SDK inicializado"?

4. ✅ Porta correta?
   - Node.js: 3000
   - Python: 5000
   - Otel Collector: 4317

**Solução:**

```bash
# Ver logs do collector
docker logs signoz-otel-collector

# Reiniciar tudo
cd /home/cleverson/Documents/signoz-lab/signoz/deploy/docker
docker-compose restart
```

### "Erro ao instalar dependências"

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

### "Porta já em uso"

**Solução 1**: Encerre o processo na porta:
```bash
# Linux
sudo lsof -ti:3000 | xargs kill -9
# ou
sudo fuser -k 3000/tcp

# Ver quais portas estão em uso
netstat -tulpn | grep LISTEN
```

**Solução 2**: Mude a porta:
```javascript
// Node.js: server.js
const PORT = process.env.PORT || 3001;  // Mudou de 3000 para 3001
```

```python
# Python: app.py
app.run(host='0.0.0.0', port=5001, debug=True)  # Mudou de 5000 para 5001
```

---

## 🎓 Próximos Passos

Agora que você sabe instrumentar aplicações, tente:

1. ✅ **Instrumentar sua própria aplicação**
   - Copie o `instrumentation.js` ou `instrumentation.py`
   - Adapte para sua stack
   - Deploy e monitoramento!

2. ✅ **Configurar Alertas**
   - No SigNoz: Settings → Alerts
   - Configure notificações para erros

3. ✅ **Integrar com CI/CD**
   - Adicione testes de observabilidade
   - Deploy automático com monitoring

4. ✅ **Adicionar Instrumentação Customizada**
   - Spans específicos para operações críticas
   - Métricas customizadas
   - Atributos de negócio

---

## 📚 Recursos

- [Documentação SigNoz](https://signoz.io/docs/)
- [OpenTelemetry](https://opentelemetry.io/)
- [Node.js Instrumentation](https://signoz.io/docs/instrumentation/nodejs/)
- [Python Instrumentation](https://signoz.io/docs/instrumentation/python/)

---

## ✨ Dicas

💡 **Dica 1**: Execute ambos Node.js e Python ao mesmo tempo para comparar!

💡 **Dica 2**: Use load testing para gerar mais dados:
```bash
# Instalar Apache Bench
sudo apt-get install apache2-utils  # Linux
brew install httpd                   # Mac

# Gerar carga
ab -n 1000 -c 10 http://localhost:3000/api/health
```

💡 **Dica 3**: Explore diferentes cenários:
- Requisições normais
- Requisições lentas
- Requisições com erro
- Muitas requisições rápidas

Divirta-se explorando observabilidade! 🚀


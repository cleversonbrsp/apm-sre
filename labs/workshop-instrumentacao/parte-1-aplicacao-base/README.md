# 📦 Parte 1: Criando a Aplicação Base

**Objetivo:** Criar uma aplicação web simples SEM instrumentação (ainda!)

---

## 🎯 O Que Vamos Criar

Uma API simples de gerenciamento de tarefas (TODO) com:
- ✅ Listar tarefas
- ✅ Criar tarefa
- ✅ Marcar como concluída
- ✅ Simular operações lentas
- ✅ Simular erros

---

## 🟢 Opção 1: Node.js

### Passo 1.1: Criar diretório

```bash
cd workshop-instrumentacao/parte-1-aplicacao-base
mkdir meu-projeto-nodejs
cd meu-projeto-nodejs
```

### Passo 1.2: Inicializar projeto

```bash
npm init -y
```

### Passo 1.3: Instalar Express

```bash
npm install express
```

### Passo 1.4: Criar aplicação

Crie o arquivo `app.js`:

```javascript
const express = require('express');
const app = express();

app.use(express.json());

// "Banco de dados" em memória
let tasks = [
  { id: 1, title: 'Aprender SigNoz', completed: false },
  { id: 2, title: 'Instrumentar aplicação', completed: false },
];

let nextId = 3;

// ============================================================================
// ROTAS
// ============================================================================

// Listar todas as tarefas
app.get('/tasks', (req, res) => {
  console.log('📋 Listando tarefas');
  res.json(tasks);
});

// Criar nova tarefa
app.post('/tasks', (req, res) => {
  const { title } = req.body;
  
  if (!title) {
    return res.status(400).json({ error: 'Título é obrigatório' });
  }
  
  const task = {
    id: nextId++,
    title,
    completed: false,
  };
  
  tasks.push(task);
  console.log(`✅ Tarefa criada: ${title}`);
  
  res.status(201).json(task);
});

// Marcar tarefa como concluída
app.put('/tasks/:id/complete', (req, res) => {
  const id = parseInt(req.params.id);
  const task = tasks.find(t => t.id === id);
  
  if (!task) {
    return res.status(404).json({ error: 'Tarefa não encontrada' });
  }
  
  task.completed = true;
  console.log(`✓ Tarefa concluída: ${task.title}`);
  
  res.json(task);
});

// Operação lenta (simula chamada externa)
app.get('/tasks/sync', async (req, res) => {
  console.log('🔄 Sincronizando tarefas (operação lenta)...');
  
  // Simula delay de 2 segundos
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  console.log('✅ Sincronização concluída');
  res.json({ message: 'Tarefas sincronizadas', count: tasks.length });
});

// Endpoint com erro
app.get('/tasks/export', (req, res) => {
  console.log('📤 Exportando tarefas...');
  
  // Simula 30% de chance de erro
  if (Math.random() < 0.3) {
    console.error('❌ Erro ao exportar tarefas');
    return res.status(500).json({ error: 'Erro ao conectar com serviço de exportação' });
  }
  
  res.json({ 
    message: 'Tarefas exportadas com sucesso',
    tasks: tasks 
  });
});

// Rota raiz
app.get('/', (req, res) => {
  res.json({
    message: '📝 API de Tarefas',
    endpoints: {
      'GET /tasks': 'Listar tarefas',
      'POST /tasks': 'Criar tarefa',
      'PUT /tasks/:id/complete': 'Marcar como concluída',
      'GET /tasks/sync': 'Sincronizar (lento)',
      'GET /tasks/export': 'Exportar (pode falhar)',
    }
  });
});

// ============================================================================
// SERVIDOR
// ============================================================================

const PORT = 3001;

app.listen(PORT, () => {
  console.log(`\n🚀 Servidor rodando em http://localhost:${PORT}`);
  console.log('\n📋 Endpoints disponíveis:');
  console.log('   GET  /tasks              - Listar tarefas');
  console.log('   POST /tasks              - Criar tarefa');
  console.log('   PUT  /tasks/:id/complete - Marcar como concluída');
  console.log('   GET  /tasks/sync         - Sincronizar (lento)');
  console.log('   GET  /tasks/export       - Exportar (pode falhar)');
  console.log('\n💡 Esta aplicação ainda NÃO está instrumentada!\n');
});
```

### Passo 1.5: Executar

```bash
node app.js
```

### Passo 1.6: Testar

Em outro terminal:

```bash
# Listar tarefas
curl http://localhost:3001/tasks

# Criar tarefa
curl -X POST http://localhost:3001/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Minha primeira tarefa"}'

# Marcar como concluída
curl -X PUT http://localhost:3001/tasks/1/complete

# Operação lenta
curl http://localhost:3001/tasks/sync

# Pode falhar (tente várias vezes)
curl http://localhost:3001/tasks/export
```

---

## 🐍 Opção 2: Python

### Passo 1.1: Criar diretório

```bash
cd workshop-instrumentacao/parte-1-aplicacao-base
mkdir meu-projeto-python
cd meu-projeto-python
```

### Passo 1.2: Criar ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

### Passo 1.3: Instalar Flask

```bash
pip install Flask
```

### Passo 1.4: Criar aplicação

Crie o arquivo `app.py`:

```python
from flask import Flask, request, jsonify
import time
import random

app = Flask(__name__)

# "Banco de dados" em memória
tasks = [
    {'id': 1, 'title': 'Aprender SigNoz', 'completed': False},
    {'id': 2, 'title': 'Instrumentar aplicação', 'completed': False},
]

next_id = 3

# ============================================================================
# ROTAS
# ============================================================================

@app.route('/')
def home():
    return jsonify({
        'message': '📝 API de Tarefas',
        'endpoints': {
            'GET /tasks': 'Listar tarefas',
            'POST /tasks': 'Criar tarefa',
            'PUT /tasks/<id>/complete': 'Marcar como concluída',
            'GET /tasks/sync': 'Sincronizar (lento)',
            'GET /tasks/export': 'Exportar (pode falhar)',
        }
    })

@app.route('/tasks', methods=['GET'])
def list_tasks():
    print('📋 Listando tarefas')
    return jsonify(tasks)

@app.route('/tasks', methods=['POST'])
def create_task():
    global next_id
    
    data = request.get_json()
    title = data.get('title')
    
    if not title:
        return jsonify({'error': 'Título é obrigatório'}), 400
    
    task = {
        'id': next_id,
        'title': title,
        'completed': False,
    }
    
    tasks.append(task)
    next_id += 1
    
    print(f'✅ Tarefa criada: {title}')
    return jsonify(task), 201

@app.route('/tasks/<int:task_id>/complete', methods=['PUT'])
def complete_task(task_id):
    task = next((t for t in tasks if t['id'] == task_id), None)
    
    if not task:
        return jsonify({'error': 'Tarefa não encontrada'}), 404
    
    task['completed'] = True
    print(f'✓ Tarefa concluída: {task["title"]}')
    
    return jsonify(task)

@app.route('/tasks/sync', methods=['GET'])
def sync_tasks():
    print('🔄 Sincronizando tarefas (operação lenta)...')
    
    # Simula delay de 2 segundos
    time.sleep(2)
    
    print('✅ Sincronização concluída')
    return jsonify({
        'message': 'Tarefas sincronizadas',
        'count': len(tasks)
    })

@app.route('/tasks/export', methods=['GET'])
def export_tasks():
    print('📤 Exportando tarefas...')
    
    # Simula 30% de chance de erro
    if random.random() < 0.3:
        print('❌ Erro ao exportar tarefas')
        return jsonify({'error': 'Erro ao conectar com serviço de exportação'}), 500
    
    return jsonify({
        'message': 'Tarefas exportadas com sucesso',
        'tasks': tasks
    })

# ============================================================================
# SERVIDOR
# ============================================================================

if __name__ == '__main__':
    print('\n🚀 Servidor rodando em http://localhost:5001')
    print('\n📋 Endpoints disponíveis:')
    print('   GET  /tasks              - Listar tarefas')
    print('   POST /tasks              - Criar tarefa')
    print('   PUT  /tasks/<id>/complete - Marcar como concluída')
    print('   GET  /tasks/sync         - Sincronizar (lento)')
    print('   GET  /tasks/export       - Exportar (pode falhar)')
    print('\n💡 Esta aplicação ainda NÃO está instrumentada!\n')
    
    app.run(host='0.0.0.0', port=5001, debug=True)
```

### Passo 1.5: Executar

```bash
python app.py
```

### Passo 1.6: Testar

```bash
# Listar tarefas
curl http://localhost:5001/tasks

# Criar tarefa
curl -X POST http://localhost:5001/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Minha primeira tarefa"}'

# Marcar como concluída
curl -X PUT http://localhost:5001/tasks/1/complete

# Operação lenta
curl http://localhost:5001/tasks/sync

# Pode falhar
curl http://localhost:5001/tasks/export
```

---

## ✅ Checklist

- [ ] Aplicação criada
- [ ] Dependências instaladas
- [ ] Aplicação executando
- [ ] Todos os endpoints testados e funcionando
- [ ] Você entendeu o que cada rota faz

---

## 🎯 Observações Importantes

### O Que Temos Até Agora

✅ Uma aplicação web funcional  
✅ Múltiplos endpoints  
✅ Operações síncronas e assíncronas  
✅ Tratamento de erros  
✅ Logs no console  

### O Que NÃO Temos

❌ Não conseguimos ver traces  
❌ Não conseguimos medir latência  
❌ Não conseguimos rastrear requests entre serviços  
❌ Não conseguimos debugar facilmente  
❌ Não temos métricas no SigNoz  

**Por quê?** Porque ainda não adicionamos instrumentação!

---

## 🚀 Próximo Passo

Agora que você tem uma aplicação funcionando, vamos instrumentá-la!

**Continue em:** `../parte-2-primeira-instrumentacao/README.md`

---

## 💡 Dicas

1. **Mantenha a aplicação rodando** para testar depois da instrumentação
2. **Anote mentalmente** onde você acha que seria útil ter traces
3. **Pense:** Quais operações você gostaria de rastrear?

**Na próxima parte, você vai adicionar OpenTelemetry manualmente!** 🎉


# 🎨 Parte 3: Criando Spans Customizados

**Objetivo:** Adicionar seus próprios spans para rastrear operações específicas!

---

## 🎯 Por Que Criar Spans Customizados?

A auto-instrumentação rastreia HTTP, DB, etc. Mas e operações do **seu negócio**?

Exemplos:
- Processar pagamento
- Validar dados
- Enviar email
- Calcular recomendações
- Gerar relatório

**Spans customizados** permitem rastrear QUALQUER operação!

---

## 🟢 Node.js

### Passo 3.1: Importar API do OpenTelemetry

No arquivo `app.js`, adicione NO INÍCIO (depois dos requires):

```javascript
const express = require('express');
const { trace } = require('@opentelemetry/api');

const app = express();
```

### Passo 3.2: Criar Uma Função com Span Customizado

Adicione esta função ANTES das rotas:

```javascript
// Função que simula validação de tarefa
function validateTask(title) {
  // Obter tracer
  const tracer = trace.getTracer('meu-todo-app');
  
  // Criar span customizado
  const span = tracer.startSpan('validar_tarefa');
  
  try {
    // Adicionar atributo
    span.setAttribute('task.title', title);
    span.setAttribute('validation.type', 'title_check');
    
    // Simular validação (delay de 50ms)
    const start = Date.now();
    while (Date.now() - start < 50) {
      // Processamento...
    }
    
    // Validação
    if (title.length < 3) {
      span.setAttribute('validation.result', 'failed');
      span.setAttribute('validation.reason', 'title_too_short');
      throw new Error('Título muito curto');
    }
    
    if (title.length > 100) {
      span.setAttribute('validation.result', 'failed');
      span.setAttribute('validation.reason', 'title_too_long');
      throw new Error('Título muito longo');
    }
    
    span.setAttribute('validation.result', 'success');
    return true;
    
  } catch (error) {
    // Marcar span com erro
    span.recordException(error);
    span.setStatus({ code: 2, message: error.message }); // 2 = ERROR
    throw error;
    
  } finally {
    // SEMPRE finalizar o span!
    span.end();
  }
}
```

### Passo 3.3: Usar o Span na Rota

Modifique a rota `POST /tasks` para usar a validação:

```javascript
app.post('/tasks', (req, res) => {
  const { title } = req.body;
  
  if (!title) {
    return res.status(400).json({ error: 'Título é obrigatório' });
  }
  
  try {
    // Validar com span customizado
    validateTask(title);
    
    const task = {
      id: nextId++,
      title,
      completed: false,
    };
    
    tasks.push(task);
    console.log(`✅ Tarefa criada: ${title}`);
    
    res.status(201).json(task);
    
  } catch (error) {
    console.error(`❌ Erro na validação: ${error.message}`);
    return res.status(400).json({ error: error.message });
  }
});
```

### Passo 3.4: Criar Operação com Sub-Spans

Adicione uma nova rota com múltiplos spans aninhados:

```javascript
// Processar múltiplas tarefas
app.post('/tasks/batch', async (req, res) => {
  const { titles } = req.body;
  
  if (!titles || !Array.isArray(titles)) {
    return res.status(400).json({ error: 'Envie um array de títulos' });
  }
  
  const tracer = trace.getTracer('meu-todo-app');
  
  // Span principal
  const mainSpan = tracer.startSpan('processar_lote_tarefas');
  mainSpan.setAttribute('batch.size', titles.length);
  
  const created = [];
  const errors = [];
  
  for (let i = 0; i < titles.length; i++) {
    // Sub-span para cada tarefa
    const taskSpan = tracer.startSpan(`processar_tarefa_${i+1}`, {
      parent: mainSpan,
    });
    
    try {
      taskSpan.setAttribute('task.index', i);
      taskSpan.setAttribute('task.title', titles[i]);
      
      // Validar
      validateTask(titles[i]);
      
      // Criar
      const task = {
        id: nextId++,
        title: titles[i],
        completed: false,
      };
      
      tasks.push(task);
      created.push(task);
      
      taskSpan.setAttribute('task.created_id', task.id);
      taskSpan.setStatus({ code: 1 }); // OK
      
    } catch (error) {
      errors.push({ title: titles[i], error: error.message });
      taskSpan.recordException(error);
      taskSpan.setStatus({ code: 2, message: error.message });
      
    } finally {
      taskSpan.end();
    }
  }
  
  mainSpan.setAttribute('batch.created', created.length);
  mainSpan.setAttribute('batch.errors', errors.length);
  mainSpan.end();
  
  res.status(201).json({
    created: created,
    errors: errors,
    summary: {
      total: titles.length,
      success: created.length,
      failed: errors.length,
    }
  });
});
```

### Passo 3.5: Reiniciar e Testar

```bash
# Ctrl+C para parar
npm start
```

Teste os novos spans:

```bash
# Criar tarefa válida
curl -X POST http://localhost:3001/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Tarefa com validação customizada"}'

# Criar tarefa inválida (título curto)
curl -X POST http://localhost:3001/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"aa"}'

# Criar lote
curl -X POST http://localhost:3001/tasks/batch \
  -H "Content-Type: application/json" \
  -d '{"titles":["Tarefa 1","aa","Tarefa 3 com nome válido","x"]}'
```

### Passo 3.6: Ver no SigNoz

1. Acesse: http://localhost:8080
2. Vá em **Traces**
3. Procure por `POST /tasks` ou `POST /tasks/batch`
4. Clique em um trace

Você verá:

```
POST /tasks/batch                    [201] 250ms
├─ processar_lote_tarefas            200ms
│  ├─ processar_tarefa_1              50ms
│  │  └─ validar_tarefa               45ms
│  ├─ processar_tarefa_2              50ms
│  │  └─ validar_tarefa (ERROR!)      45ms
│  ├─ processar_tarefa_3              50ms
│  │  └─ validar_tarefa               45ms
│  └─ processar_tarefa_4              50ms
│     └─ validar_tarefa (ERROR!)      45ms
```

---

## 🐍 Python

### Passo 3.1: Importar API do OpenTelemetry

No arquivo `app.py`, adicione:

```python
import instrumentation

from flask import Flask, request, jsonify
from opentelemetry import trace  # ← Adicione esta linha
import time
import random
```

### Passo 3.2: Criar Função com Span Customizado

Adicione antes das rotas:

```python
def validate_task(title):
    """Valida uma tarefa com span customizado"""
    tracer = trace.get_tracer(__name__)
    
    with tracer.start_as_current_span("validar_tarefa") as span:
        # Adicionar atributos
        span.set_attribute("task.title", title)
        span.set_attribute("validation.type", "title_check")
        
        # Simular processamento
        time.sleep(0.05)
        
        # Validação
        if len(title) < 3:
            span.set_attribute("validation.result", "failed")
            span.set_attribute("validation.reason", "title_too_short")
            raise ValueError("Título muito curto")
        
        if len(title) > 100:
            span.set_attribute("validation.result", "failed")
            span.set_attribute("validation.reason", "title_too_long")
            raise ValueError("Título muito longo")
        
        span.set_attribute("validation.result", "success")
        return True
```

### Passo 3.3: Usar o Span na Rota

Modifique `POST /tasks`:

```python
@app.route('/tasks', methods=['POST'])
def create_task():
    global next_id
    
    data = request.get_json()
    title = data.get('title')
    
    if not title:
        return jsonify({'error': 'Título é obrigatório'}), 400
    
    try:
        # Validar com span customizado
        validate_task(title)
        
        task = {
            'id': next_id,
            'title': title,
            'completed': False,
        }
        
        tasks.append(task)
        next_id += 1
        
        print(f'✅ Tarefa criada: {title}')
        return jsonify(task), 201
        
    except ValueError as e:
        print(f'❌ Erro na validação: {e}')
        return jsonify({'error': str(e)}), 400
```

### Passo 3.4: Criar Operação com Sub-Spans

Adicione nova rota:

```python
@app.route('/tasks/batch', methods=['POST'])
def create_batch():
    global next_id
    
    data = request.get_json()
    titles = data.get('titles', [])
    
    if not isinstance(titles, list):
        return jsonify({'error': 'Envie um array de títulos'}), 400
    
    tracer = trace.get_tracer(__name__)
    
    with tracer.start_as_current_span("processar_lote_tarefas") as main_span:
        main_span.set_attribute("batch.size", len(titles))
        
        created = []
        errors = []
        
        for i, title in enumerate(titles):
            with tracer.start_as_current_span(f"processar_tarefa_{i+1}") as task_span:
                try:
                    task_span.set_attribute("task.index", i)
                    task_span.set_attribute("task.title", title)
                    
                    # Validar
                    validate_task(title)
                    
                    # Criar
                    task = {
                        'id': next_id,
                        'title': title,
                        'completed': False,
                    }
                    
                    tasks.append(task)
                    created.append(task)
                    next_id += 1
                    
                    task_span.set_attribute("task.created_id", task['id'])
                    
                except ValueError as e:
                    errors.append({'title': title, 'error': str(e)})
        
        main_span.set_attribute("batch.created", len(created))
        main_span.set_attribute("batch.errors", len(errors))
    
    return jsonify({
        'created': created,
        'errors': errors,
        'summary': {
            'total': len(titles),
            'success': len(created),
            'failed': len(errors),
        }
    }), 201
```

### Passo 3.5: Testar

```bash
python app.py
```

```bash
# Tarefa válida
curl -X POST http://localhost:5001/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Tarefa com validação customizada"}'

# Tarefa inválida
curl -X POST http://localhost:5001/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"aa"}'

# Lote
curl -X POST http://localhost:5001/tasks/batch \
  -H "Content-Type: application/json" \
  -d '{"titles":["Tarefa 1","aa","Tarefa 3 válida","x"]}'
```

---

## ✅ Checklist

- [ ] Importou API do OpenTelemetry
- [ ] Criou função com span customizado
- [ ] Adicionou atributos ao span
- [ ] Testou validação com sucesso e erro
- [ ] Criou operação com sub-spans
- [ ] Viu spans customizados no SigNoz
- [ ] Entendeu hierarquia de spans

---

## 🎓 O Que Você Aprendeu

✅ Como criar spans customizados  
✅ Como adicionar atributos  
✅ Como criar hierarquia de spans (parent/child)  
✅ Como marcar spans com erro  
✅ Como usar `with` (Python) ou `try/finally` (Node)  
✅ Quando usar spans customizados vs auto-instrumentação  

---

## 🚀 Próximo Passo

Agora você domina spans customizados!

Na próxima parte, você vai aprender a adicionar **atributos ricos** para tornar seus traces ainda mais úteis!

**Continue em:** `../parte-4-atributos-avancados/README.md` (em breve)

---

## 💡 Dicas

1. **Use spans customizados** para lógica de negócio importante
2. **Adicione atributos** relevantes para debug
3. **Crie hierarquia** para operações complexas
4. **SEMPRE finalize** os spans (`span.end()` ou `with`)
5. **Marque erros** para facilitar troubleshooting


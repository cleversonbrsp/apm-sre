# 🎨 Part 3: Creating Custom Spans

**Goal:** Extend your instrumentation with spans that map directly to your business logic.

---

## 🎯 Why Add Custom Spans?

Auto-instrumentation already traces HTTP handlers, database drivers, queues, and more—but it does not know how your domain works. When you need visibility into:

- Payment flows
- Data validation
- Email delivery
- Recommendation engines
- Report generation

…custom spans are the way to go. They let you trace anything you deem important.

---

## 🟢 Node.js

### Step 3.1 – Import the OpenTelemetry API

At the top of `app.js`, after your existing requires:

```javascript
const express = require('express');
const { trace } = require('@opentelemetry/api');

const app = express();
```

### Step 3.2 – Create a Function That Emits a Custom Span

Place this helper **before** your route declarations:

```javascript
// Simulate validating a task while emitting a custom span
function validateTask(title) {
  const tracer = trace.getTracer('my-todo-app');
  const span = tracer.startSpan('validate_task');

  try {
    span.setAttribute('task.title', title);
    span.setAttribute('validation.type', 'title_check');

    // Simulate work (50 ms CPU loop)
    const start = Date.now();
    while (Date.now() - start < 50) {
      // Busy wait to mimic processing
    }

    if (title.length < 3) {
      span.setAttribute('validation.result', 'failed');
      span.setAttribute('validation.reason', 'title_too_short');
      throw new Error('Title too short');
    }

    if (title.length > 100) {
      span.setAttribute('validation.result', 'failed');
      span.setAttribute('validation.reason', 'title_too_long');
      throw new Error('Title too long');
    }

    span.setAttribute('validation.result', 'success');
    return true;
  } catch (error) {
    span.recordException(error);
    span.setStatus({ code: 2, message: error.message }); // 2 = ERROR
    throw error;
  } finally {
    span.end();
  }
}
```

### Step 3.3 – Use the Span in `POST /tasks`

Update the route so validation emits telemetry:

```javascript
app.post('/tasks', (req, res) => {
  const { title } = req.body;

  if (!title) {
    return res.status(400).json({ error: 'Title is required' });
  }

  try {
    validateTask(title);

    const task = {
      id: nextId++,
      title,
      completed: false,
    };

    tasks.push(task);
    console.log(`✅ Task created: ${title}`);

    res.status(201).json(task);
  } catch (error) {
    console.error(`❌ Validation error: ${error.message}`);
    return res.status(400).json({ error: error.message });
  }
});
```

### Step 3.4 – Add a Batch Endpoint with Nested Spans

Create spans for the overall batch **and** each individual item:

```javascript
app.post('/tasks/batch', async (req, res) => {
  const { titles } = req.body;

  if (!titles || !Array.isArray(titles)) {
    return res.status(400).json({ error: 'Send an array of titles' });
  }

  const tracer = trace.getTracer('my-todo-app');
  const mainSpan = tracer.startSpan('process_task_batch');
  mainSpan.setAttribute('batch.size', titles.length);

  const created = [];
  const errors = [];

  for (let index = 0; index < titles.length; index++) {
    const taskSpan = tracer.startSpan(`process_task_${index + 1}`, {
      parent: mainSpan,
    });

    try {
      taskSpan.setAttribute('task.index', index);
      taskSpan.setAttribute('task.title', titles[index]);

      validateTask(titles[index]);

      const task = {
        id: nextId++,
        title: titles[index],
        completed: false,
      };

      tasks.push(task);
      created.push(task);

      taskSpan.setAttribute('task.created_id', task.id);
      taskSpan.setStatus({ code: 1 }); // OK
    } catch (error) {
      errors.push({ title: titles[index], error: error.message });
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
    created,
    errors,
    summary: {
      total: titles.length,
      success: created.length,
      failed: errors.length,
    },
  });
});
```

### Step 3.5 – Restart and Exercise the Endpoints

```bash
# Stop and start the server
npm start
```

```bash
# Valid task
curl -X POST http://localhost:3001/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Task with custom validation"}'

# Invalid task (title too short)
curl -X POST http://localhost:3001/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"aa"}'

# Batch request (mix of valid and invalid)
curl -X POST http://localhost:3001/tasks/batch \
  -H "Content-Type: application/json" \
  -d '{"titles":["Task 1","aa","Task 3 valid name","x"]}'
```

### Step 3.6 – Inspect in SigNoz

1. Open http://localhost:8080  
2. Navigate to **Traces**  
3. Filter for `POST /tasks` or `POST /tasks/batch`  
4. Open a trace to view the span tree

You should see a waterfall similar to:

```
POST /tasks/batch                    [201] 250ms
├─ process_task_batch                200ms
│  ├─ process_task_1                  50ms
│  │  └─ validate_task                45ms
│  ├─ process_task_2                  50ms
│  │  └─ validate_task (ERROR!)       45ms
│  ├─ process_task_3                  50ms
│  │  └─ validate_task                45ms
│  └─ process_task_4                  50ms
│     └─ validate_task (ERROR!)       45ms
```

---

## 🐍 Python

### Step 3.1 – Import the OpenTelemetry API

In `app.py`:

```python
import instrumentation

from flask import Flask, request, jsonify
from opentelemetry import trace
import time
import random
```

### Step 3.2 – Create a Function with a Custom Span

Place this helper above your routes:

```python
def validate_task(title: str) -> bool:
    """Validate a task while emitting a custom span."""
    tracer = trace.get_tracer(__name__)

    with tracer.start_as_current_span("validate_task") as span:
        span.set_attribute("task.title", title)
        span.set_attribute("validation.type", "title_check")

        time.sleep(0.05)

        if len(title) < 3:
            span.set_attribute("validation.result", "failed")
            span.set_attribute("validation.reason", "title_too_short")
            raise ValueError("Title too short")

        if len(title) > 100:
            span.set_attribute("validation.result", "failed")
            span.set_attribute("validation.reason", "title_too_long")
            raise ValueError("Title too long")

        span.set_attribute("validation.result", "success")
        return True
```

### Step 3.3 – Use the Span in `POST /tasks`

Update the route:

```python
@app.route('/tasks', methods=['POST'])
def create_task():
    global next_id

    data = request.get_json()
    title = data.get('title')

    if not title:
        return jsonify({'error': 'Title is required'}), 400

    try:
        validate_task(title)

        task = {
            'id': next_id,
            'title': title,
            'completed': False,
        }

        tasks.append(task)
        next_id += 1

        print(f'✅ Task created: {title}')
        return jsonify(task), 201

    except ValueError as exc:
        print(f'❌ Validation error: {exc}')
        return jsonify({'error': str(exc)}), 400
```

### Step 3.4 – Build a Batch Endpoint with Child Spans

```python
@app.route('/tasks/batch', methods=['POST'])
def create_batch():
    global next_id

    data = request.get_json()
    titles = data.get('titles', [])

    if not isinstance(titles, list):
        return jsonify({'error': 'Send an array of titles'}), 400

    tracer = trace.get_tracer(__name__)

    with tracer.start_as_current_span("process_task_batch") as main_span:
        main_span.set_attribute("batch.size", len(titles))

        created = []
        errors = []

        for index, title in enumerate(titles):
            with tracer.start_as_current_span(f"process_task_{index + 1}") as task_span:
                try:
                    task_span.set_attribute("task.index", index)
                    task_span.set_attribute("task.title", title)

                    validate_task(title)

                    task = {
                        'id': next_id,
                        'title': title,
                        'completed': False,
                    }

                    tasks.append(task)
                    created.append(task)
                    next_id += 1

                    task_span.set_attribute("task.created_id", task['id'])
                except ValueError as exc:
                    errors.append({'title': title, 'error': str(exc)})

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

### Step 3.5 – Run and Exercise the Endpoints

```bash
python app.py
```

```bash
# Valid task
curl -X POST http://localhost:5001/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Task with custom validation"}'

# Invalid task
curl -X POST http://localhost:5001/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"aa"}'

# Batch
curl -X POST http://localhost:5001/tasks/batch \
  -H "Content-Type: application/json" \
  -d '{"titles":["Task 1","aa","Task 3 valid","x"]}'
```

---

## ✅ Checklist

- [ ] Imported the OpenTelemetry API  
- [ ] Created a helper that emits custom spans  
- [ ] Added useful attributes to spans  
- [ ] Tested both success and failure paths  
- [ ] Built an operation with parent/child spans  
- [ ] Confirmed spans appear in SigNoz  
- [ ] Understand how span hierarchies model workflows  

---

## 🎓 What You Learned

✅ Creating custom spans  
✅ Attaching attributes for context  
✅ Modeling parent/child span hierarchies  
✅ Recording exceptions and marking spans as errors  
✅ Using `try/finally` (Node.js) and `with` (Python) safely  
✅ Deciding when to use custom spans vs. auto instrumentation  

---

## 🚀 Next Step

You now control your observability story. Next up: **richer attributes** to make traces even more valuable.

**Continue with:** `../part-4-advanced-attributes/README.md` *(coming soon)*.

---

## 💡 Tips

1. Wrap critical business logic in custom spans  
2. Add attributes that answer debugging questions  
3. Build span hierarchies for multi-step flows  
4. Always end spans (`span.end()` or `with`)  
5. Record errors to streamline troubleshooting  


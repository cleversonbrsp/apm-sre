#  Part 1: Build the Base Application

**Goal:** Create a simple web application with NO instrumentation (yet!)

---

##  What We Will Build

A very small TODO management API with:
-  List tasks
-  Create tasks
-  Mark a task as completed
-  Simulated slow operations
-  Simulated failures

---

##  Option 1: Node.js

### Step 1.1: Create a directory

```bash
cd workshop-instrumentation/part-1-base-application
mkdir my-nodejs-project
cd my-nodejs-project
```

### Step 1.2: Initialize the project

```bash
npm init -y
```

### Step 1.3: Install Express

```bash
npm install express
```

### Step 1.4: Create the application

Create the file `app.js`:

```javascript
const express = require('express');
const app = express();

app.use(express.json());

// In-memory "database"
let tasks = [
  { id: 1, title: 'Learn SigNoz', completed: false },
  { id: 2, title: 'Instrument the application', completed: false },
];

let nextId = 3;

// ============================================================================
// ROUTES
// ============================================================================

// List all tasks
app.get('/tasks', (req, res) => {
  console.log(' Listing tasks');
  res.json(tasks);
});

// Create a new task
app.post('/tasks', (req, res) => {
  const { title } = req.body;
  
  if (!title) {
    return res.status(400).json({ error: 'Title is required' });
  }
  
  const task = {
    id: nextId++,
    title,
    completed: false,
  };
  
  tasks.push(task);
  console.log(` Task created: ${title}`);
  
  res.status(201).json(task);
});

// Mark a task as completed
app.put('/tasks/:id/complete', (req, res) => {
  const id = parseInt(req.params.id);
  const task = tasks.find(t => t.id === id);
  
  if (!task) {
    return res.status(404).json({ error: 'Task not found' });
  }
  
  task.completed = true;
  console.log(` Task completed: ${task.title}`);
  
  res.json(task);
});

// Slow operation (simulate external call)
app.get('/tasks/sync', async (req, res) => {
  console.log(' Syncing tasks (slow operation)…');
  
  // Simulate 2-second delay
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  console.log(' Sync complete');
  res.json({ message: 'Tasks synced', count: tasks.length });
});

// Endpoint with simulated failure
app.get('/tasks/export', (req, res) => {
  console.log(' Exporting tasks…');
  
  // Fail 30% of the time
  if (Math.random() < 0.3) {
    console.error(' Error exporting tasks');
    return res.status(500).json({ error: 'Failed to connect to export service' });
  }
  
  res.json({ 
    message: 'Tasks exported successfully',
    tasks: tasks 
  });
});

// Root route
app.get('/', (req, res) => {
  res.json({
    message: ' Tasks API',
    endpoints: {
      'GET /tasks': 'List tasks',
      'POST /tasks': 'Create task',
      'PUT /tasks/:id/complete': 'Mark as completed',
      'GET /tasks/sync': 'Sync (slow)',
      'GET /tasks/export': 'Export (may fail)',
    }
  });
});

// ============================================================================
// SERVER
// ============================================================================

const PORT = 3001;

app.listen(PORT, () => {
  console.log(`\n Server running at http://localhost:${PORT}`);
  console.log('\n Available endpoints:');
  console.log('   GET  /tasks              - List tasks');
  console.log('   POST /tasks              - Create task');
  console.log('   PUT  /tasks/:id/complete - Mark as completed');
  console.log('   GET  /tasks/sync         - Sync (slow)');
  console.log('   GET  /tasks/export       - Export (may fail)');
  console.log('\n This application is NOT instrumented yet!\n');
});
```

### Step 1.5: Run it

```bash
node app.js
```

### Step 1.6: Test it

In another terminal:

```bash
# List tasks
curl http://localhost:3001/tasks

# Create a task
curl -X POST http://localhost:3001/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"My first task"}'

# Mark as completed
curl -X PUT http://localhost:3001/tasks/1/complete

# Slow operation
curl http://localhost:3001/tasks/sync

# Might fail (try multiple times)
curl http://localhost:3001/tasks/export
```

---

##  Option 2: Python

### Step 1.1: Create a directory

```bash
cd workshop-instrumentation/part-1-base-application
mkdir my-python-project
cd my-python-project
```

### Step 1.2: Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 1.3: Install Flask

```bash
pip install Flask
```

### Step 1.4: Create the application

Create the file `app.py`:

```python
from flask import Flask, request, jsonify
import time
import random

app = Flask(__name__)

# In-memory "database"
tasks = [
    {'id': 1, 'title': 'Learn SigNoz', 'completed': False},
    {'id': 2, 'title': 'Instrument the application', 'completed': False},
]

next_id = 3

# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def home():
    return jsonify({
        'message': ' Tasks API',
        'endpoints': {
            'GET /tasks': 'List tasks',
            'POST /tasks': 'Create task',
            'PUT /tasks/<id>/complete': 'Mark as completed',
            'GET /tasks/sync': 'Sync (slow)',
            'GET /tasks/export': 'Export (may fail)',
        }
    })

@app.route('/tasks', methods=['GET'])
def list_tasks():
    print(' Listing tasks')
    return jsonify(tasks)

@app.route('/tasks', methods=['POST'])
def create_task():
    global next_id
    
    data = request.get_json()
    title = data.get('title')
    
    if not title:
        return jsonify({'error': 'Title is required'}), 400
    
    task = {
        'id': next_id,
        'title': title,
        'completed': False,
    }
    
    tasks.append(task)
    next_id += 1
    
    print(f' Task created: {title}')
    return jsonify(task), 201

@app.route('/tasks/<int:task_id>/complete', methods=['PUT'])
def complete_task(task_id):
    task = next((t for t in tasks if t['id'] == task_id), None)
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    task['completed'] = True
    print(f' Task completed: {task["title"]}')
    
    return jsonify(task)

@app.route('/tasks/sync', methods=['GET'])
def sync_tasks():
    print(' Syncing tasks (slow operation)…')
    
    # Simulate a 2 second delay
    time.sleep(2)
    
    print(' Sync complete')
    return jsonify({
        'message': 'Tasks synced',
        'count': len(tasks)
    })

@app.route('/tasks/export', methods=['GET'])
def export_tasks():
    print(' Exporting tasks…')
    
    # 30% failure chance
    if random.random() < 0.3:
        print(' Error exporting tasks')
        return jsonify({'error': 'Failed to connect to export service'}), 500
    
    return jsonify({
        'message': 'Tasks exported successfully',
        'tasks': tasks
    })

# ============================================================================
# SERVER
# ============================================================================

if __name__ == '__main__':
    print('\n Server running at http://localhost:5001')
    print('\n Available endpoints:')
    print('   GET  /tasks              - List tasks')
    print('   POST /tasks              - Create task')
    print('   PUT  /tasks/<id>/complete - Mark as completed')
    print('   GET  /tasks/sync         - Sync (slow)')
    print('   GET  /tasks/export       - Export (may fail)')
    print('\n This application is NOT instrumented yet!\n')
    
    app.run(host='0.0.0.0', port=5001, debug=True)
```

### Step 1.5: Run it

```bash
python app.py
```

### Step 1.6: Test it

```bash
# List tasks
curl http://localhost:5001/tasks

# Create a task
curl -X POST http://localhost:5001/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"My first task"}'

# Mark as completed
curl -X PUT http://localhost:5001/tasks/1/complete

# Slow operation
curl http://localhost:5001/tasks/sync

# May fail
curl http://localhost:5001/tasks/export
```

---

##  Checklist

- [ ] Application created
- [ ] Dependencies installed
- [ ] App running
- [ ] Every endpoint tested and working
- [ ] You understand what each route does

---

##  Key Takeaways

### What We Have So Far

 A working web application  
 Multiple endpoints  
 Both synchronous and asynchronous operations  
 Error handling  
 Console logs  

### What We DON’T Have Yet

 No visibility into traces  
 No latency measurements  
 No way to follow requests across services  
 Debugging is still painful  
 No metrics inside SigNoz  

**Why?** Because we haven’t added instrumentation yet!

---

##  Next Step

Now that the app works, let’s instrument it.

**Continue with:** `../part-2-first-instrumentation/README.md`

---

##  Tips

1. **Keep the application running** so you can test after instrumentation  
2. **Take note** of where traces would already be useful  
3. **Think ahead:** Which operations do you want to monitor?  

**In the next part you’ll add OpenTelemetry manually!** 


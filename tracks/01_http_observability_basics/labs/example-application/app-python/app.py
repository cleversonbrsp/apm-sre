"""
 PYTHON + FLASK SAMPLE APPLICATION

This REST API demonstrates:
- Standard routes
- A simulated datastore
- Different request patterns
- Purpose-built endpoints to highlight observability
"""

#  IMPORTANT: import instrumentation BEFORE Flask!
# This makes sure auto-instrumentation hooks are active.
import instrumentation  # noqa: F401

from flask import Flask, request, jsonify
import time
import random
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask application
app = Flask(__name__)


# ----------------------------------------------------------------------------
# MOCK DATABASE
# ----------------------------------------------------------------------------

users = [
    {'id': 1, 'name': 'Alice Smith', 'email': 'alice@example.com', 'role': 'admin'},
    {'id': 2, 'name': 'Bob Johnson', 'email': 'bob@example.com', 'role': 'user'},
    {'id': 3, 'name': 'Carol Davis', 'email': 'carol@example.com', 'role': 'user'},
]

products = [
    {'id': 1, 'name': 'Laptop', 'price': 2999.99, 'stock': 15},
    {'id': 2, 'name': 'Wireless Mouse', 'price': 89.90, 'stock': 50},
    {'id': 3, 'name': 'Mechanical Keyboard', 'price': 199.90, 'stock': 30},
]


# ----------------------------------------------------------------------------
# API ROUTES
# ----------------------------------------------------------------------------

@app.route('/api/health', methods=['GET'])
def health_check():
    """
     HEALTH CHECK

    Lightweight endpoint to confirm the service is alive.
    Automatically traced by OpenTelemetry!
    """
    return jsonify({
        'status': 'healthy',
        'service': 'signoz-example-python',
        'version': '1.0.0',
    })


@app.route('/api/users', methods=['GET'])
def list_users():
    """
     LIST USERS

    Returns every user in the mock database.
    Demonstrates successful request traces.
    """
    logger.info(' Listing all users')

    # Simulate database latency
    time.sleep(0.1)

    return jsonify({
        'count': len(users),
        'users': users,
    })


@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """
     GET USER BY ID

    Returns a single user and enriches traces with metadata.
    """
    logger.info(f' Looking up user ID: {user_id}')

    user = next((u for u in users if u['id'] == user_id), None)

    if not user:
        logger.warning(f' User not found: {user_id}')
        return jsonify({
            'error': 'User not found',
            'requestedId': user_id,
        }), 404

    logger.info(f' User found: {user["name"]}')
    return jsonify(user)


@app.route('/api/users', methods=['POST'])
def create_user():
    """
     CREATE USER

    Adds a new user and illustrates write operations.
    """
    data = request.get_json()

    if not data or not data.get('name') or not data.get('email'):
        return jsonify({
            'error': 'Name and email are required',
        }), 400

    name = data['name']
    email = data['email']

    logger.info(f' Creating user: {name} ({email})')

    new_user = {
        'id': len(users) + 1,
        'name': name,
        'email': email,
        'role': data.get('role', 'user'),
    }

    users.append(new_user)

    logger.info(f' User created successfully: ID {new_user["id"]}')
    return jsonify({
        'message': 'User created successfully',
        'user': new_user,
    }), 201


@app.route('/api/products', methods=['GET'])
def list_products():
    """
     LIST PRODUCTS (WITH RANDOM FAILURES)

    Randomly fails to demonstrate error tracing.
    """
    logger.info(' Listing products…')

    # 20% failure rate to highlight error handling
    if random.random() < 0.2:
        logger.error(' Failed to fetch products from the database')
        return jsonify({
            'error': 'Internal error fetching products',
            'message': 'Database connection failed',
        }), 500

    return jsonify({
        'count': len(products),
        'products': products,
    })


@app.route('/api/slow', methods=['GET'])
def slow_endpoint():
    """
     SLOW ENDPOINT

    Simulates a slow operation (e.g., expensive query or external call).
    Perfect to visualize latency in traces.
    """
    logger.info(' Starting slow operation…')

    # Simulate a 1–3 second delay
    delay = 1 + random.random() * 2
    time.sleep(delay)

    logger.info(f' Slow operation completed in {delay:.0f}s')

    return jsonify({
        'message': 'Slow operation completed',
        'duration': f'{delay:.0f}s',
    })


@app.route('/api/random-error', methods=['GET'])
def random_error():
    """
     RANDOM ERROR

    Randomly returns success, 404, or 500 responses.
    Demonstrates error tracing and status codes.
    """
    outcome = random.choice(['404', '500', 'success'])
    logger.info(f' Emitting response type: {outcome}')

    if outcome == '404':
        return jsonify({
            'error': 'Resource not found',
            'type': 'NotFound',
        }), 404
    if outcome == '500':
        return jsonify({
            'error': 'Internal server error',
            'type': 'InternalServerError',
        }), 500

    return jsonify({
        'message': 'Success!',
        'type': 'Success',
    })


# ----------------------------------------------------------------------------
# ERROR HANDLER
# ----------------------------------------------------------------------------

@app.errorhandler(Exception)
def handle_exception(error):
    """
     ERROR HANDLER

    Catch-all for uncaught exceptions; returns JSON responses.
    """
    logger.exception(' Unhandled exception')
    return jsonify({
        'error': 'Internal server error',
        'message': str(error),
    }), 500


# ----------------------------------------------------------------------------
# ROOT ROUTE
# ----------------------------------------------------------------------------

@app.route('/', methods=['GET'])
def root():
    """
     ROOT ENDPOINT

    Provides a quick overview of the API.
    """
    return jsonify({
        'message': ' Python API instrumented with OpenTelemetry',
        'version': '1.0.0',
        'endpoints': {
            'GET /api/health': 'Health check',
            'GET /api/users': 'List users',
            'GET /api/users/<id>': 'Get user by ID',
            'POST /api/users': 'Create user',
            'GET /api/products': 'List products (20% error rate)',
            'GET /api/slow': 'Simulate slow operation',
            'GET /api/random-error': 'Return random errors',
        },
        'signoz': 'http://localhost:8080',
        'instrumentation': 'OpenTelemetry auto instrumentation',
    })


# ----------------------------------------------------------------------------
# APPLICATION ENTRY POINT
# ----------------------------------------------------------------------------

if __name__ == '__main__':
    print('\n Flask server running at http://localhost:5001')
    print('\n Available endpoints:')
    print('   GET  /api/health         - Health check')
    print('   GET  /api/users          - List users')
    print('   GET  /api/users/<id>     - Get user by ID')
    print('   POST /api/users          - Create user')
    print('   GET  /api/products       - List products (20% error rate)')
    print('   GET  /api/slow           - Slow operation')
    print('   GET  /api/random-error   - Random error generator')
    print('\n Tip: Open http://localhost:8080 to explore telemetry in SigNoz!\n')

    app.run(host='0.0.0.0', port=5001, debug=True)


"""
🌐 APLICAÇÃO EXEMPLO PYTHON + FLASK

Esta aplicação demonstra uma API RESTful com:
- Rotas de API
- Simulação de banco de dados
- Diferentes tipos de operações
- Alguns endpoints com propósito de mostrar observabilidade
"""

# ⚡ IMPORTANTE: Importe o instrumentation ANTES do Flask!
# Isso garante que a auto-instrumentação funcione corretamente
import instrumentation  # noqa: F401

from flask import Flask, request, jsonify
import time
import random
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criar aplicação Flask
app = Flask(__name__)


# ----------------------------------------------------------------------------
# MOCK DATABASE
# ----------------------------------------------------------------------------

users = [
    {'id': 1, 'name': 'Alice Silva', 'email': 'alice@example.com', 'role': 'admin'},
    {'id': 2, 'name': 'Bob Souza', 'email': 'bob@example.com', 'role': 'user'},
    {'id': 3, 'name': 'Carol Costa', 'email': 'carol@example.com', 'role': 'user'},
]

products = [
    {'id': 1, 'name': 'Laptop', 'price': 2999.99, 'stock': 15},
    {'id': 2, 'name': 'Mouse', 'price': 89.90, 'stock': 50},
    {'id': 3, 'name': 'Teclado', 'price': 199.90, 'stock': 30},
]


# ----------------------------------------------------------------------------
# ROTAS DA API
# ----------------------------------------------------------------------------

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    🏥 HEALTH CHECK
    
    Endpoint básico para verificar se a aplicação está rodando
    Rastreado automaticamente pelo OpenTelemetry!
    """
    return jsonify({
        'status': 'healthy',
        'service': 'signoz-example-python',
        'version': '1.0.0',
    })


@app.route('/api/users', methods=['GET'])
def list_users():
    """
    👥 LISTAR USUÁRIOS
    
    Retorna todos os usuários
    Mostra traces de operações bem-sucedidas
    """
    logger.info('📋 Listando todos os usuários')
    
    # Simula delay de banco de dados
    time.sleep(0.1)
    
    return jsonify({
        'count': len(users),
        'users': users,
    })


@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """
    👤 BUSCAR USUÁRIO POR ID
    
    Retorna um usuário específico
    Mostra traces com atributos customizados
    """
    logger.info(f'🔍 Buscando usuário ID: {user_id}')
    
    user = next((u for u in users if u['id'] == user_id), None)
    
    if not user:
        logger.warning(f'❌ Usuário não encontrado: {user_id}')
        return jsonify({
            'error': 'Usuário não encontrado',
            'requestedId': user_id,
        }), 404
    
    logger.info(f'✅ Usuário encontrado: {user["name"]}')
    return jsonify(user)


@app.route('/api/users', methods=['POST'])
def create_user():
    """
    ➕ CRIAR NOVO USUÁRIO
    
    Adiciona um novo usuário
    Mostra traces de operações de escrita
    """
    data = request.get_json()
    
    if not data or not data.get('name') or not data.get('email'):
        return jsonify({
            'error': 'Nome e email são obrigatórios',
        }), 400
    
    name = data['name']
    email = data['email']
    
    logger.info(f'➕ Criando novo usuário: {name} ({email})')
    
    new_user = {
        'id': len(users) + 1,
        'name': name,
        'email': email,
        'role': data.get('role', 'user'),
    }
    
    users.append(new_user)
    
    logger.info(f'✅ Usuário criado com sucesso: ID {new_user["id"]}')
    return jsonify({
        'message': 'Usuário criado com sucesso',
        'user': new_user,
    }), 201


@app.route('/api/products', methods=['GET'])
def list_products():
    """
    🛍️ LISTAR PRODUTOS (COM ERRO)
    
    Este endpoint simula um erro ocasional
    Perfeito para ver rastreamento de erros no SigNoz!
    """
    logger.info('🛍️ Listando produtos...')
    
    # Simula 20% de chance de erro
    if random.random() < 0.2:
        logger.error('❌ Erro ao buscar produtos do banco')
        return jsonify({
            'error': 'Erro interno ao buscar produtos',
            'message': 'Falha na conexão com o banco de dados',
        }), 500
    
    return jsonify({
        'count': len(products),
        'products': products,
    })


@app.route('/api/slow', methods=['GET'])
def slow_endpoint():
    """
    🐌 ENDPOINT LENTO
    
    Simula uma operação lenta (ex: query complexa, integração externa)
    Perfeito para ver traces de performance e identificar gargalos!
    """
    logger.info('🐌 Iniciando operação lenta...')
    
    # Simula delay de 1-3 segundos (tipo de query complexa)
    delay = 1 + random.random() * 2
    
    time.sleep(delay)
    
    logger.info(f'✅ Operação lenta concluída em {delay:.0f}s')
    
    return jsonify({
        'message': 'Operação lenta concluída',
        'duration': f'{delay:.0f}s',
    })


@app.route('/api/random-error', methods=['GET'])
def random_error():
    """
    🎲 ERRO ALEATÓRIO
    
    Gera diferentes tipos de erros aleatoriamente
    Demonstra rastreamento de erros e status codes
    """
    error_type = random.choice(['404', '500', 'success'])
    
    logger.info(f'🎲 Gerando resposta tipo: {error_type}')
    
    if error_type == '404':
        return jsonify({
            'error': 'Recurso não encontrado',
            'type': 'NotFound',
        }), 404
    elif error_type == '500':
        return jsonify({
            'error': 'Erro interno do servidor',
            'type': 'InternalServerError',
        }), 500
    else:
        return jsonify({
            'message': 'Sucesso!',
            'type': 'Success',
        })


# ----------------------------------------------------------------------------
# MIDDLEWARE DE ERRO
# ----------------------------------------------------------------------------

@app.errorhandler(404)
def not_found(error):
    logger.warning(f'❌ Rota não encontrada: {request.path}')
    return jsonify({
        'error': 'Rota não encontrada',
        'path': request.path,
    }), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f'❌ Erro interno: {error}')
    return jsonify({
        'error': 'Erro interno do servidor',
        'message': str(error),
    }), 500


# ----------------------------------------------------------------------------
# INICIALIZAÇÃO DO SERVIDOR
# ----------------------------------------------------------------------------

if __name__ == '__main__':
    print('\n🚀 Servidor iniciado!')
    print('📡 Servidor rodando em: http://localhost:5000')
    print('\n📋 Endpoints disponíveis:')
    print('   GET  /api/health              - Health check')
    print('   GET  /api/users               - Lista usuários')
    print('   GET  /api/users/<id>          - Busca usuário')
    print('   POST /api/users               - Cria usuário')
    print('   GET  /api/products            - Lista produtos (20% erro)')
    print('   GET  /api/random-error        - Erro aleatório')
    print('   GET  /api/slow                - Operação lenta')
    print('\n💡 Dica: Agora acesse http://localhost:8080 para ver os dados no SigNoz!\n')
    
    app.run(host='0.0.0.0', port=5000, debug=True)


"""
📚 CONCEITOS DE OBSERVABILIDADE DEMONSTRADOS:

1. ✅ Traces automáticos de todas as requisições HTTP
2. ✅ Spans para cada operação (DB, delays, etc)
3. ✅ Rastreamento de erros (status 404, 500, etc)
4. ✅ Métricas de performance (latência, throughput)
5. ✅ Contexto HTTP propagado automaticamente
6. ✅ Logs estruturados

🎯 TUDO ISSO SEM MODIFICAR MANUALMENTE CADA ENDPOINT!
O OpenTelemetry faz a mágica automaticamente! ✨
"""


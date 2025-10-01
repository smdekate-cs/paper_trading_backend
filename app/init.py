from flask import Flask
from flask_socketio import SocketIO
from flask_jwt_extended import JWTManager
from pymongo import MongoClient
import redis
import os

# Initialize extensions
socketio = SocketIO()
jwt = JWTManager()
redis_client = None
mongo_client = None

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config.from_pyfile('config.py')
    
    # Initialize extensions
    socketio.init_app(app, cors_allowed_origins="*", message_queue=app.config['REDIS_URL'])
    jwt.init_app(app)
    
    # Initialize databases
    global mongo_client, redis_client
    mongo_client = MongoClient(app.config['MONGO_URI'])
    redis_client = redis.from_url(app.config['REDIS_URL'])
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.portfolio import portfolio_bp
    from app.routes.trades import trades_bp
    from app.routes.market import market_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(portfolio_bp, url_prefix='/portfolio')
    app.register_blueprint(trades_bp, url_prefix='/trades')
    app.register_blueprint(market_bp, url_prefix='/market')
    
    # WebSocket events
    @socketio.on('connect')
    def handle_connect():
        print('Client connected')
        emit('connection_status', {'status': 'connected'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        print('Client disconnected')
    
    @socketio.on('subscribe_market_data')
    def handle_subscribe_market_data(data):
        symbol = data.get('symbol')
        if symbol:
            # In a real implementation, you'd add to a room
            emit('market_data', {
                'symbol': symbol,
                'data': market_data_service.get_live_price(symbol)
            })
    
    @socketio.on('unsubscribe_market_data')
    def handle_unsubscribe_market_data(data):
        symbol = data.get('symbol')
        # Remove from room implementation
    
    return app
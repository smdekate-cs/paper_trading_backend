from flask import Blueprint, request, jsonify
from app.services.market_data import market_data_service

market_bp = Blueprint('market', __name__)

@market_bp.route('/live/<symbol>', methods=['GET'])
def get_live_price(symbol):
    try:
        price_data = market_data_service.get_live_price(symbol.upper())
        
        if not price_data:
            return jsonify({'error': 'Failed to fetch market data'}), 500
        
        return jsonify({
            'symbol': symbol,
            'data': price_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@market_bp.route('/indices', methods=['GET'])
def get_indices():
    try:
        indices_data = market_data_service.get_index_data()
        
        return jsonify({
            'indices': indices_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
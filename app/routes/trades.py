from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.trade import Trade, TradeType, TradeStatus
from app.models.portfolio import Portfolio
from app.services.market_data import market_data_service

trades_bp = Blueprint('trades', __name__)

@trades_bp.route('/create', methods=['POST'])
@jwt_required()
def create_trade():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validation
        required_fields = ['symbol', 'trade_type', 'quantity']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Get current market price
        market_data = market_data_service.get_live_price(data['symbol'])
        if not market_data:
            return jsonify({'error': 'Failed to fetch market price'}), 500
        
        entry_price = market_data['price']
        quantity = data['quantity']
        margin_used = entry_price * quantity
        
        # Check portfolio margin
        portfolio = Portfolio.find_by_user_id(current_user_id)
        if not portfolio:
            return jsonify({'error': 'Portfolio not found. Create a portfolio first.'}), 404
        
        if portfolio.available_margin < margin_used:
            return jsonify({'error': 'Insufficient margin'}), 400
        
        # Create trade
        trade = Trade(
            user_id=current_user_id,
            symbol=data['symbol'],
            trade_type=data['trade_type'],
            quantity=quantity,
            entry_price=entry_price,
            margin_used=margin_used,
            stop_loss=data.get('stop_loss'),
            target_price=data.get('target_price')
        )
        
        trade.save()
        
        # Update portfolio margin
        portfolio.update_margin(margin_used)
        
        return jsonify({
            'message': 'Trade created successfully',
            'trade': trade.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@trades_bp.route('/active', methods=['GET'])
@jwt_required()
def get_active_trades():
    try:
        current_user_id = get_jwt_identity()
        trades = Trade.find_active_trades_by_user(current_user_id)
        
        return jsonify({
            'trades': [trade.to_dict() for trade in trades]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@trades_bp.route('/history', methods=['GET'])
@jwt_required()
def get_trade_history():
    try:
        current_user_id = get_jwt_identity()
        trades = Trade.find_all_trades_by_user(current_user_id)
        
        return jsonify({
            'trades': [trade.to_dict() for trade in trades]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
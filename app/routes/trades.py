from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.trade import Trade, TradeType, TradeStatus
from app.models.portfolio import Portfolio
from app.services.market_data import market_data_service
from app.services.notification_service import notification_service
from app.models.user import User

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
    
    user = User.find_by_client_id(current_user_id)
    if user:
        trade_dict = trade.to_dict()
        notification_service.notify_trade_creation(
            user.email, 
            user.phone, 
            trade_dict
        )


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

@trades_bp.route('/performance/<user_id>', methods=['GET'])
@jwt_required()
def get_trade_performance(user_id):
    try:
        current_user_id = get_jwt_identity()
        
        # Users can only access their own performance
        if user_id != current_user_id:
            return jsonify({'error': 'Unauthorized access'}), 403
        
        portfolio = Portfolio.find_by_user_id(user_id)
        if not portfolio:
            return jsonify({'error': 'Portfolio not found'}), 404
        
        all_trades = Trade.find_all_trades_by_user(user_id)
        active_trades = Trade.find_active_trades_by_user(user_id)
        
        # Calculate performance metrics
        total_trades = len(all_trades)
        active_trades_count = len(active_trades)
        closed_trades_count = total_trades - active_trades_count
        
        # Calculate win rate
        profitable_trades = [t for t in all_trades if t.pnl > 0 and t.status != TradeStatus.ACTIVE]
        win_rate = (len(profitable_trades) / closed_trades_count * 100) if closed_trades_count > 0 else 0
        
        # Calculate total PnL
        total_pnl = sum(trade.pnl for trade in all_trades)
        active_pnl = sum(trade.pnl for trade in active_trades)
        
        # Calculate average trade metrics
        avg_profit = sum(trade.pnl for trade in profitable_trades) / len(profitable_trades) if profitable_trades else 0
        
        return jsonify({
            'performance': {
                'portfolio_summary': portfolio.to_dict(),
                'trade_statistics': {
                    'total_trades': total_trades,
                    'active_trades': active_trades_count,
                    'closed_trades': closed_trades_count,
                    'win_rate': round(win_rate, 2),
                    'total_pnl': total_pnl,
                    'active_pnl': active_pnl,
                    'average_profit': round(avg_profit, 2),
                    'profitable_trades': len(profitable_trades)
                },
                'margin_utilization': {
                    'available_margin': portfolio.available_margin,
                    'utilized_margin': portfolio.utilized_margin,
                    'utilization_percentage': round(
                        (portfolio.utilized_margin / (portfolio.available_margin + portfolio.utilized_margin)) * 100, 2
                    ) if (portfolio.available_margin + portfolio.utilized_margin) > 0 else 0
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@trades_bp.route('/exit/<trade_id>', methods=['POST'])
@jwt_required()
def exit_trade(trade_id):
    try:
        current_user_id = get_jwt_identity()
        
        trade = Trade.find_by_id(trade_id)
        if not trade:
            return jsonify({'error': 'Trade not found'}), 404
        
        # Check ownership
        if trade.user_id != current_user_id:
            return jsonify({'error': 'Unauthorized access'}), 403
        
        # Check if trade is already closed
        if trade.status != TradeStatus.ACTIVE:
            return jsonify({'error': 'Trade is already closed'}), 400
        
        # Get current market price
        market_data = market_data_service.get_live_price(trade.symbol)
        if not market_data:
            return jsonify({'error': 'Failed to fetch market price'}), 500
        
        exit_price = market_data['price']
        
        # Close trade
        trade.close_trade(exit_price, TradeStatus.CLOSED)
        
        # Update portfolio
        portfolio = Portfolio.find_by_user_id(current_user_id)
        if portfolio:
            portfolio.update_margin(-trade.margin_used, trade.pnl)
        
        return jsonify({
            'message': 'Trade exited successfully',
            'trade': trade.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@trades_bp.route('/exit-all/<user_id>', methods=['POST'])
@jwt_required()
def exit_all_trades(user_id):
    try:
        current_user_id = get_jwt_identity()
        
        # Check authorization
        if user_id != current_user_id:
            return jsonify({'error': 'Unauthorized access'}), 403
        
        active_trades = Trade.find_active_trades_by_user(user_id)
        
        if not active_trades:
            return jsonify({'error': 'No active trades found'}), 404
        
        exited_trades = []
        total_pnl = 0
        total_margin_freed = 0
        
        for trade in active_trades:
            # Get current market price
            market_data = market_data_service.get_live_price(trade.symbol)
            if market_data:
                exit_price = market_data['price']
                trade.close_trade(exit_price, TradeStatus.CLOSED)
                exited_trades.append(trade.to_dict())
                total_pnl += trade.pnl
                total_margin_freed += trade.margin_used
        
        # Update portfolio
        portfolio = Portfolio.find_by_user_id(user_id)
        if portfolio:
            portfolio.update_margin(-total_margin_freed, total_pnl)
        
        return jsonify({
            'message': f'All {len(exited_trades)} trades exited successfully',
            'exited_trades': exited_trades,
            'total_pnl': total_pnl,
            'margin_freed': total_margin_freed
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
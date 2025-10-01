from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.portfolio import Portfolio

portfolio_bp = Blueprint('portfolio', __name__)

@portfolio_bp.route('/create', methods=['POST'])
@jwt_required()
def create_portfolio():
    try:
        current_user_id = get_jwt_identity()
        
        # Check if portfolio already exists
        existing_portfolio = Portfolio.find_by_user_id(current_user_id)
        if existing_portfolio:
            return jsonify({'error': 'Portfolio already exists for this user'}), 409
        
        data = request.get_json()
        initial_margin = data.get('initial_margin', 100000.0)
        
        # Validate initial margin
        if initial_margin <= 0:
            return jsonify({'error': 'Initial margin must be positive'}), 400
        
        portfolio = Portfolio(current_user_id, initial_margin)
        portfolio.save()
        
        return jsonify({
            'message': 'Portfolio created successfully',
            'portfolio': portfolio.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@portfolio_bp.route('/<user_id>', methods=['GET'])
@jwt_required()
def get_portfolio(user_id):
    try:
        current_user_id = get_jwt_identity()
        
        # Users can only access their own portfolio
        if user_id != current_user_id:
            return jsonify({'error': 'Unauthorized access'}), 403
        
        portfolio = Portfolio.find_by_user_id(user_id)
        if not portfolio:
            return jsonify({'error': 'Portfolio not found'}), 404
        
        return jsonify({
            'portfolio': portfolio.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@portfolio_bp.route('/my-portfolio', methods=['GET'])
@jwt_required()
def get_my_portfolio():
    try:
        current_user_id = get_jwt_identity()
        
        portfolio = Portfolio.find_by_user_id(current_user_id)
        if not portfolio:
            return jsonify({'error': 'Portfolio not found. Please create a portfolio first.'}), 404
        
        return jsonify({
            'portfolio': portfolio.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
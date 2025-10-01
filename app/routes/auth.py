from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models.user import User
import uuid
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validation
        required_fields = ['name', 'email', 'phone', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if email already exists
        if User.email_exists(data['email']):
            return jsonify({'error': 'Email already registered'}), 409
        
        # Create user
        client_id = str(uuid.uuid4())[:8]  # Generate unique client ID
        password_hash = User.hash_password(data['password'])
        
        user = User(
            client_id=client_id,
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            password_hash=password_hash
        )
        
        user.save()
        
        return jsonify({
            'message': 'User registered successfully',
            'client_id': client_id,
            'user': {
                'name': user.name,
                'email': user.email,
                'phone': user.phone
            }
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        user = User.find_by_email(data['email'])
        if not user or not user.verify_password(data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Create access token
        access_token = create_access_token(identity=user.client_id)
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': {
                'client_id': user.client_id,
                'name': user.name,
                'email': user.email
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        current_user_id = get_jwt_identity()
        user = User.find_by_client_id(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'client_id': user.client_id,
            'name': user.name,
            'email': user.email,
            'phone': user.phone
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
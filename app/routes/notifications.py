from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.services.notification_service import notification_service

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/test', methods=['POST'])
@jwt_required()
def test_notification():
    try:
        data = request.get_json()
        
        email = data.get('email')
        phone = data.get('phone')
        message = data.get('message', 'Test notification from Paper Trading Platform')
        
        if email:
            notification_service.send_email(email, "Test Notification", message)
        
        if phone:
            notification_service.send_sms(phone, message)
        
        return jsonify({
            'message': 'Test notifications sent successfully',
            'email_sent': bool(email),
            'sms_sent': bool(phone)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
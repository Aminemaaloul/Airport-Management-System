from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Notification, db
from flasgger import swag_from

notification_bp = Blueprint('notification', __name__)

@notification_bp.route('/users/me/notifications', methods=['GET'])
@jwt_required()
@swag_from({
    'responses': {
        200: {
            'description': 'Retrieve all notifications for the current user.',
            'examples': {
                'application/json': {
                    'data': [
                        {
                            'id': 1,
                            'user_id': 1,
                            'flight_number': 'TU123',
                            'message': 'Your flight is delayed',
                            'timestamp': '2025-01-30T20:00:00Z'
                        }
                    ]
                }
            }
        }
    },
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'required': True,
            'type': 'string',
            'description': 'Authorization token'
        }
    ]
})
def get_my_notifications():
    """
    Retrieve all notifications for the current user.
    """
    user_id = get_jwt_identity()
    notifications = Notification.query.filter_by(user_id=user_id).order_by(Notification.timestamp.desc()).all()
    return jsonify({"data": [notification.serialize() for notification in notifications]}), 200

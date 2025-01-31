from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Baggage, db, User, FlightSubscription, Flight  # Changed
from decorators import admin_required
from flasgger import swag_from

baggage_bp = Blueprint('baggage', __name__)

@baggage_bp.route('/users/me/baggage', methods=['GET'])
@jwt_required()
@swag_from({
    'responses': {
        200: {
            'description': 'Retrieve baggage status for a specific user.',
            'examples': {
                'application/json': {
                    'data': [
                        {
                            'id': 1,
                            'user_id': 1,
                            'status': 'loaded',
                            'flight_id': 100,
                            'created_at': '2025-01-30T20:00:00Z'
                        }
                    ]
                }
            }
        },
        404: {
            'description': 'User not found',
            'examples': {
                'application/json': {
                    'message': 'User not found'
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
def get_user_baggage():
    """
    Retrieve baggage status for a specific user.
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    # corrected code : Filter Baggage based on User ID
    baggages = Baggage.query.filter_by(user_id=user_id).all()
    return jsonify({"data": [baggage.serialize() for baggage in baggages]}), 200

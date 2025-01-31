from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import AssistanceRequest, db
from datetime import datetime
from flasgger import swag_from

assistance_bp = Blueprint('assistance', __name__)

@assistance_bp.route('/assistance', methods=['POST'])
@jwt_required()
@swag_from({
    'responses': {
        201: {
            'description': 'Assistance requested successfully',
            'examples': {
                'application/json': {
                    'message': 'Assistance requested',
                    'data': {
                        'user_id': 1,
                        'request_type': 'wheelchair',
                        'flight_id': 100,
                        'status': 'pending',
                        'timestamp': '2025-01-30T20:00:00Z'
                    }
                }
            }
        },
        400: {
            'description': 'Missing required fields',
            'examples': {
                'application/json': {
                    'message': 'Missing required fields'
                }
            }
        }
    },
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'id': 'RequestAssistance',
                'required': ['request_type', 'flight_id'],
                'properties': {
                    'request_type': {
                        'type': 'string',
                        'example': 'wheelchair'
                    },
                    'flight_id': {
                        'type': 'integer',
                        'example': 100
                    }
                }
            }
        },
        {
            'name': 'Authorization',
            'in': 'header',
            'required': True,
            'type': 'string',
            'description': 'Authorization token'
        }
    ]
})
def request_assistance():
    """
    Request passenger assistance.
    """
    data = request.get_json()
    user_id = get_jwt_identity()
    request_type = data.get('request_type')
    flight_id = data.get('flight_id')
    assistance_request = AssistanceRequest(
        user_id=user_id,
        request_type=request_type,
        flight_id=flight_id,
        status="pending",
        timestamp=datetime.utcnow()
    )
    db.session.add(assistance_request)
    db.session.commit()
    return jsonify({"message": "Assistance requested", "data": assistance_request.serialize()}), 201

@assistance_bp.route('/assistance/status', methods=['GET'])
@jwt_required()
@swag_from({
    'responses': {
        200: {
            'description': 'Retrieve all assistance requests for the user',
            'examples': {
                'application/json': {
                    'data': [
                        {
                            'user_id': 1,
                            'request_type': 'wheelchair',
                            'flight_id': 100,
                            'status': 'pending',
                            'timestamp': '2025-01-30T20:00:00Z'
                        }
                    ]
                }
            }
        },
        404: {
            'description': 'No assistance requests found',
            'examples': {
                'application/json': {
                    'message': 'No assistance requests found'
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
def get_assistance_status():
    """
    Get the status of all assistance requests for the user.
    """
    user_id = get_jwt_identity()
    assistance_requests = AssistanceRequest.query.filter_by(user_id=user_id).all()
    if not assistance_requests:
        return jsonify({"message": "No assistance requests found"}), 404
    return jsonify({"data": [request.serialize() for request in assistance_requests]}), 200

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models import Flight, User, Notification, Baggage, db, AssistanceRequest, ParkingSpot
from decorators import admin_required
from datetime import datetime
from app.services.notifications import send_notification
from dateutil import parser
from flasgger import swag_from

# Create a Blueprint for admin routes
admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/flights', methods=['POST'])
@jwt_required()
@admin_required
@swag_from({
    'responses': {
        201: {
            'description': 'Flight added successfully',
            'examples': {
                'application/json': {
                    'message': 'Flight added successfully',
                    'data': {
                        'flight_number': 'TU123',
                        'departure_airport': 'Tunis Carthage International Airport',
                        'arrival_airport': 'Paris Charles de Gaulle Airport',
                        'departure_time': '2025-01-30T12:00:00Z',
                        'arrival_time': '2025-01-30T15:00:00Z',
                        'status': 'scheduled',
                        'airline': 'Tunisair'
                    }
                }
            }
        },
        400: {
            'description': 'Invalid or missing date-time format',
            'examples': {
                'application/json': {
                    'message': 'Invalid or missing date-time format'
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
                'id': 'AddFlight',
                'required': ['flight_number', 'departure_airport', 'arrival_airport', 'departure_time', 'arrival_time'],
                'properties': {
                    'flight_number': {
                        'type': 'string',
                        'example': 'TU123'
                    },
                    'departure_airport': {
                        'type': 'string',
                        'example': 'Tunis Carthage International Airport'
                    },
                    'arrival_airport': {
                        'type': 'string',
                        'example': 'Paris Charles de Gaulle Airport'
                    },
                    'departure_time': {
                        'type': 'string',
                        'example': '2025-01-30T12:00:00Z'
                    },
                    'arrival_time': {
                        'type': 'string',
                        'example': '2025-01-30T15:00:00Z'
                    },
                    'status': {
                        'type': 'string',
                        'example': 'scheduled'
                    },
                    'airline': {
                        'type': 'string',
                        'example': 'Tunisair'
                    }
                }
            }
        }
    ]
})
def add_flight():
    """
    Add a new flight (Admin only).
    """
    data = request.get_json()
    try:
        departure_time = parser.parse(data['departure_time'])
        arrival_time = parser.parse(data['arrival_time'])
    except (KeyError, ValueError):
        return jsonify({"message": "Invalid or missing date-time format"}), 400

    flight = Flight(
        flight_number=data['flight_number'],
        departure_airport=data['departure_airport'],
        arrival_airport=data['arrival_airport'],
        departure_time=departure_time,
        arrival_time=arrival_time,
        status=data.get('status', 'scheduled'),
        airline=data.get('airline', 'Unknown')
    )
    db.session.add(flight)
    db.session.commit()
    return jsonify({"message": "Flight added successfully", "data": flight.serialize()}), 201
@admin_bp.route('/admin/flights/<int:flight_id>', methods=['PUT'])
@jwt_required()
@admin_required
@swag_from({
    'responses': {
        200: {
            'description': 'Flight updated successfully',
            'examples': {
                'application/json': {
                    'message': 'Flight updated successfully',
                    'data': {
                        'flight_number': 'TU123',
                        'departure_airport': 'Tunis Carthage International Airport',
                        'arrival_airport': 'Paris Charles de Gaulle Airport',
                        'departure_time': '2025-01-30T12:00:00Z',
                        'arrival_time': '2025-01-30T15:00:00Z',
                        'status': 'delayed',
                        'delay_reason': 'Technical issue'
                    }
                }
            }
        },
        404: {
            'description': 'Flight not found',
            'examples': {
                'application/json': {
                    'message': 'Flight not found'
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
                'id': 'UpdateFlight',
                'required': ['status'],
                'properties': {
                    'status': {
                        'type': 'string',
                        'example': 'delayed'
                    },
                    'delay': {
                        'type': 'string',
                        'example': '30 minutes'
                    },
                    'delay_reason': {
                        'type': 'string',
                        'example': 'Technical issue'
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
def update_flight(flight_id):
    """
    Update flight status (Admin only).
    """
    data = request.get_json()
    flight = Flight.query.get(flight_id)
    if not flight:
        return jsonify({"message": "Flight not found"}), 404

    flight.status = data.get('status', flight.status)
    flight.delay = data.get('delay', flight.delay)
    flight.delay_reason = data.get('delay_reason', flight.delay_reason)
    db.session.commit()
    return jsonify({"message": "Flight updated successfully", "data": flight.serialize()}), 200

@admin_bp.route('/admin/flights/<int:flight_id>', methods=['DELETE'])
@jwt_required()
@admin_required
@swag_from({
    'responses': {
        200: {
            'description': 'Flight deleted successfully',
            'examples': {
                'application/json': {
                    'message': 'Flight deleted successfully'
                }
            }
        },
        404: {
            'description': 'Flight not found',
            'examples': {
                'application/json': {
                    'message': 'Flight not found'
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
def delete_flight(flight_id):
    """
    Delete a flight (Admin only).
    """
    flight = Flight.query.get(flight_id)
    if not flight:
        return jsonify({"message": "Flight not found"}), 404

    db.session.delete(flight)
    db.session.commit()
    return jsonify({"message": "Flight deleted successfully"}), 200

@admin_bp.route('/admin/users', methods=['GET'])
@jwt_required()
@admin_required
@swag_from({
    'responses': {
        200: {
            'description': 'Fetch all users (Admin only)',
            'examples': {
                'application/json': {
                    'data': [
                        {
                            'id': 1,
                            'username': 'admin',
                            'email': 'admin@example.com'
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
def get_all_users():
    """
    Fetch all users (Admin only).
    """
    users = User.query.all()
    return jsonify({"data": [user.serialize() for user in users]}), 200

@admin_bp.route('/admin/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
@admin_required
@swag_from({
    'responses': {
        200: {
            'description': 'User deleted successfully',
            'examples': {
                'application/json': {
                    'message': 'User deleted successfully'
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
def delete_user(user_id):
    """
    Delete a user (Admin only).
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully"}), 200

@admin_bp.route('/admin/notifications', methods=['POST'])
@jwt_required()
@admin_required
@swag_from({
    'responses': {
        201: {
            'description': 'Notification sent to all users',
            'examples': {
                'application/json': {
                    'message': 'Notification sent to all users'
                }
            }
        },
        400: {
            'description': 'Message is required',
            'examples': {
                'application/json': {
                    'message': 'Message is required'
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
                'id': 'SendNotification',
                'required': ['message'],
                'properties': {
                    'message': {
                        'type': 'string',
                        'example': 'Flight delayed due to weather conditions'
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
def send_notification_to_all():
    """
    Send a notification to all users (Admin only).
    """
    data = request.get_json()
    message = data.get('message')
    if not message:
        return jsonify({"message": "Message is required"}), 400

    users = User.query.all()
    for user in users:
        notification = Notification(
            user_id=user.id,
            flight_number="System",
            message=message,
            timestamp=datetime.utcnow()
        )
        db.session.add(notification)
    db.session.commit()
    return jsonify({"message": "Notification sent to all users"}), 201

@admin_bp.route('/admin/flights/<int:flight_id>/notify', methods=['POST'])
@jwt_required()
@admin_required
@swag_from({
    'responses': {
        200: {
            'description': 'Notifications sent successfully',
            'examples': {
                'application/json': {
                    'message': 'Notifications sent successfully'
                }
            }
        },
        400: {
            'description': 'Message is required',
            'examples': {
                'application/json': {
                    'message': 'Message is required'
                }
            }
        },
        404: {
            'description': 'Flight not found',
            'examples': {
                'application/json': {
                    'message': 'Flight not found'
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
                'id': 'NotifyPassengers',
                'required': ['message'],
                'properties': {
                    'message': {
                        'type': 'string',
                        'example': 'Flight TU123 is delayed'
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
def notify_passengers(flight_id):
    """
    Send notifications to passengers about flight updates (Admin only).
    """
    data = request.get_json()
    message = data.get('message')

    if not message:
        return jsonify({"message": "Message is required"}), 400
    
    flight = Flight.query.get(flight_id)
    if not flight:
        return jsonify({"message": "Flight not found"}), 404

    # Fetch passengers subscribed to this flight
    users = User.query.filter(User.subscriptions.any(flight_id=flight_id)).all()
    for user in users:
        notification = Notification(
            user_id=user.id,
            flight_number=flight.flight_number,
            message=message,
            timestamp=datetime.utcnow()
        )
        db.session.add(notification)
    db.session.commit()

    return jsonify({"message": "Notifications sent successfully"}), 200

@admin_bp.route('/admin/baggage/alert', methods=['POST'])
@jwt_required()
@admin_required
@swag_from({
    'responses': {
        200: {
            'description': 'Baggage alert sent successfully',
            'examples': {
                'application/json': {
                    'message': 'Baggage alert sent successfully'
                }
            }
        },
        400: {
            'description': 'User ID and message are required',
            'examples': {
                'application/json': {
                    'message': 'User ID and message are required'
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
                'id': 'BaggageAlert',
                'required': ['user_id', 'message'],
                'properties': {
                    'user_id': {
                        'type': 'integer',
                        'example': 1
                    },
                    'message': {
                        'type': 'string',
                        'example': 'Your baggage is ready for pickup'
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
def send_baggage_alert():
    """
    Send an alert to a passenger about their baggage status (Admin only).
    """
    data = request.get_json()
    user_id = data.get('user_id')
    message = data.get('message')

    if not user_id or not message:
        return jsonify({"message": "User ID and message are required"}), 400

    # Send a notification
    send_notification(user_id, message)

    return jsonify({"message": "Baggage alert sent successfully"}), 200

@admin_bp.route('/admin/assistance', methods=['GET'])
@jwt_required()
@admin_required
@swag_from({
    'responses': {
        200: {
            'description': 'Get all assistance requests.',
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
def get_all_assistance_requests():
    """
    Get all assistance requests.
    """
    assistance_requests = AssistanceRequest.query.all()
    return jsonify({"data": [request.serialize() for request in assistance_requests]}), 200

@admin_bp.route('/admin/assistance/<int:request_id>', methods=['PUT'])
@jwt_required()
@admin_required
@swag_from({
    'responses': {
        200: {
            'description': 'Assistance request updated successfully',
            'examples': {
                'application/json': {
                    'message': 'Assistance request updated',
                    'data': {
                        'user_id': 1,
                        'request_type': 'wheelchair',
                        'flight_id': 100,
                        'status': 'completed',
                        'timestamp': '2025-01-30T20:00:00Z'
                    }
                }
            }
        },
        400: {
            'description': 'Status is required',
            'examples': {
                'application/json': {
                    'message': 'Status is required'
                }
            }
        },
        404: {
            'description': 'Assistance request not found',
            'examples': {
                'application/json': {
                    'message': 'Assistance request not found'
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
                'id': 'UpdateAssistanceRequest',
                'required': ['status'],
                'properties': {
                    'status': {
                        'type': 'string',
                        'example': 'completed'
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
def update_assistance_request(request_id):
    """
    Update assistance request status.
    """
    data = request.get_json()
    status = data.get('status')
    if not status:
        return jsonify({"message": "Status is required"}), 400
    
    assistance_request = AssistanceRequest.query.get(request_id)
    if not assistance_request:
        return jsonify({"message": "Assistance request not found"}), 404
    
    assistance_request.status = status
    db.session.commit()
    return jsonify({"message": "Assistance request updated", "data": assistance_request.serialize()}), 200

@admin_bp.route('/admin/baggage/<int:baggage_id>', methods=['PUT'])
@jwt_required()
@admin_required
@swag_from({
    'responses': {
        200: {
            'description': 'Baggage updated successfully',
            'examples': {
                'application/json': {
                    'message': 'Baggage updated',
                    'data': {
                        'id': 1,
                        'user_id': 1,
                        'status': 'loaded',
                        'flight_id': 100,
                        'created_at': '2025-01-30T20:00:00Z'
                    }
                }
            }
        },
        400: {
            'description': 'Status is required',
            'examples': {
                'application/json': {
                    'message': 'Status is required'
                }
            }
        },
        404: {
            'description': 'Baggage not found',
            'examples': {
                'application/json': {
                    'message': 'Baggage not found'
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
                'id': 'UpdateBaggage',
                'required': ['status'],
                'properties': {
                    'status': {
                        'type': 'string',
                        'example': 'loaded'
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
def update_baggage(baggage_id):
    """
    Update baggage details, such as status.
    """
    data = request.get_json()
    status = data.get('status')
    if not status:
        return jsonify({"message": "Status is required"}), 400

    baggage = Baggage.query.get(baggage_id)
    if not baggage:
        return jsonify({"message": "Baggage not found"}), 404

    baggage.status = status
    db.session.commit()
    return jsonify({"message": "Baggage updated", "data": baggage.serialize()}), 200

@admin_bp.route('/admin/parking', methods=['GET'])
@jwt_required()
@admin_required
@swag_from({
    'responses': {
        200: {
            'description': 'Get all parking spots.',
            'examples': {
                'application/json': {
                    'data': [
                        {
                            'id': 1,
                            'status': 'available',
                            'location': 'P1',
                            'created_at': '2025-01-30T20:00:00Z'
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
def get_all_parking_spots():
    """
    Get all parking spots.
    """
    parking_spots = ParkingSpot.query.all()
    return jsonify({"data": [spot.serialize() for spot in parking_spots]}), 200

@admin_bp.route('/admin/parking/<int:spot_id>', methods=['PUT'])
@jwt_required()
@admin_required
@swag_from({
    'responses': {
        200: {
            'description': 'Parking spot updated successfully',
            'examples': {
                'application/json': {
                    'message': 'Parking spot updated',
                    'data': {
                        'id': 1,
                        'status': 'reserved',
                        'location': 'P1',
                        'created_at': '2025-01-30T20:00:00Z'
                    }
                }
            }
        },
        400: {
            'description': 'Status is required',
            'examples': {
                'application/json': {
                    'message': 'Status is required'
                }
            }
        },
        404: {
            'description': 'Spot not found',
            'examples': {
                'application/json': {
                    'message': 'Spot not found'
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
                'id': 'UpdateParkingSpot',
                'required': ['status'],
                'properties': {
                    'status': {
                        'type': 'string',
                        'example': 'reserved'
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
def update_parking_spot(spot_id):
    """
    Update the status of a parking spot.
    """
    data = request.get_json()
    status = data.get('status')
    if not status:
        return jsonify({"message": "Status is required"}), 400

    parking_spot = ParkingSpot.query.get(spot_id)
    if not parking_spot:
        return jsonify({"message": "Spot not found"}), 404
    
    parking_spot.status = status
    db.session.commit()
    return jsonify({"message": "Parking spot updated", "data": parking_spot.serialize()}), 200

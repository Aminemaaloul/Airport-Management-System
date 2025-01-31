from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import ParkingSpot, db, ParkingReservation, User
from decorators import admin_required
from datetime import datetime
from flasgger import swag_from

parking_bp = Blueprint('parking', __name__)

@parking_bp.route('/parking/availability', methods=['GET'])
@jwt_required()
@swag_from({
    'responses': {
        200: {
            'description': 'Check available parking spots.',
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
def check_parking_availability():
    """
    Check available parking spots.
    """
    parking_spots = ParkingSpot.query.filter_by(status='available').all()
    return jsonify({"data": [spot.serialize() for spot in parking_spots]}), 200

@parking_bp.route('/parking/reserve', methods=['POST'])
@jwt_required()
@swag_from({
    'responses': {
        200: {
            'description': 'Reserve a parking spot.',
            'examples': {
                'application/json': {
                    'message': 'Parking spot reserved',
                    'data': {
                        'user_id': 1,
                        'parking_spot_id': 1,
                        'reservation_time': '2025-01-30T20:00:00Z'
                    }
                }
            }
        },
        400: {
            'description': 'Spot not available',
            'examples': {
                'application/json': {
                    'message': 'Spot not available'
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
                'id': 'ReserveParking',
                'required': ['spot_id'],
                'properties': {
                    'spot_id': {
                        'type': 'integer',
                        'example': 1
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
def reserve_parking():
    """
    Reserve a parking spot.
    """
    data = request.get_json()
    spot_id = data.get('spot_id')
    user_id = get_jwt_identity()
    parking_spot = ParkingSpot.query.get(spot_id)
    if not parking_spot or parking_spot.status != 'available':
        return jsonify({"message": "Spot not available"}), 400
    
    parking_spot.status = 'reserved'
    parking_reservation = ParkingReservation(
      user_id=user_id,
      parking_spot_id=spot_id,
      reservation_time=datetime.utcnow()
    )
    db.session.add(parking_reservation)
    db.session.commit()
    return jsonify({"message": "Parking spot reserved", "data": parking_reservation.serialize()}), 200

@parking_bp.route('/parking/<int:spot_id>/cancel', methods=['PUT'])
@jwt_required()
@swag_from({
    'responses': {
        200: {
            'description': 'Cancel a parking reservation.',
            'examples': {
                'application/json': {
                    'message': 'Parking reservation canceled successfully'
                }
            }
        },
        404: {
            'description': 'Reservation not found',
            'examples': {
                'application/json': {
                    'message': 'Reservation not found'
                }
            }
        },
        400: {
            'description': 'This spot is not reserved',
            'examples': {
                'application/json': {
                    'message': 'This spot is not reserved'
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
def cancel_parking_reservation(spot_id):
    """
    Cancel a parking reservation.
    """
    user_id = get_jwt_identity()
    parking_spot = ParkingSpot.query.get(spot_id)
    if not parking_spot:
        return jsonify({"message": "Reservation not found"}), 404
    
    parking_reservation = ParkingReservation.query.filter_by(parking_spot_id=spot_id, user_id=user_id).first()
    if not parking_reservation:
        return jsonify({"message": "Reservation not found for this user"}), 404
    
    if parking_spot.status != 'reserved':
        return jsonify({"message": "This spot is not reserved"}), 400

    parking_spot.status = 'available'
    db.session.delete(parking_reservation)
    db.session.commit()
    return jsonify({"message": "Parking reservation canceled successfully"}), 200

@parking_bp.route('/users/me/parking', methods=['GET'])
@jwt_required()
@swag_from({
    'responses': {
        200: {
            'description': 'Get all parking spots reserved by the current user.',
            'examples': {
                'application/json': {
                    'data': [
                        {
                            'user_id': 1,
                            'parking_spot_id': 1,
                            'reservation_time': '2025-01-30T20:00:00Z'
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
def get_user_parking_spots():
    """
    Get all parking spots reserved by the current user.
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    parking_reservations = ParkingReservation.query.filter_by(user_id=user_id).all()
    return jsonify({"data": [reservation.serialize() for reservation in parking_reservations]}), 200


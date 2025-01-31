from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Flight, db, User, FlightSubscription
from app.services.flight_service import fetch_flight_data_tunis
from flasgger import swag_from

# Create a Blueprint for flight routes
flights_bp = Blueprint('flights', __name__)

@flights_bp.route('/flights', methods=['GET'])
@jwt_required()
@swag_from({
    'responses': {
        200: {
            'description': 'Fetch real-time flight data from the external API.',
            'examples': {
                'application/json': {
                    'data': [
                        {
                            'flight_number': 'TU123',
                            'departure_airport': 'Tunis Carthage International Airport',
                            'arrival_airport': 'Paris Charles de Gaulle Airport',
                            'departure_time': '2025-01-30T12:00:00Z',
                            'arrival_time': '2025-01-30T15:00:00Z',
                            'status': 'scheduled',
                            'airline': 'Tunisair'
                        }
                    ]
                }
            }
        },
        404: {
            'description': 'No flight data found',
            'examples': {
                'application/json': {
                    'message': 'No flight data found'
                }
            }
        }
    },
    'parameters': [
        {
            'name': 'date',
            'in': 'query',
            'type': 'string',
            'description': 'Optional: Specify a date for the flight data',
            'required': False
        },
        {
            'name': 'flight_number',
            'in': 'query',
            'type': 'string',
            'description': 'Optional: Retrieve flight by flight number',
            'required': False
        }
    ]
})
def get_flights():
    """
    Fetch real-time flight data from the external API.
    """
    date = request.args.get('date')  # Optional: Specify a date for the flight data
    flight_number = request.args.get('flight_number')  # Optional: Retrieve flight by flight number
    print("get_flights route hit")

    # Fetch flight data from the external API
    flights = fetch_flight_data_tunis(flight_number=flight_number, date=date)
    print("flights:", flights)

    if not flights:
        return jsonify({"message": "No flight data found"}), 404

    return jsonify({"data": flights}), 200

@flights_bp.route('/flights/<int:flight_id>', methods=['GET'])
@jwt_required()
@swag_from({
    'responses': {
        200: {
            'description': 'Retrieve specific flight details, including baggage information.',
            'examples': {
                'application/json': {
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
def get_flight_details(flight_id):
    """
    Retrieve specific flight details, including baggage information.
    """
    flight = Flight.query.get(flight_id)
    if not flight:
        return jsonify({"message": "Flight not found"}), 404

    return jsonify({"data": flight.serialize()}), 200

@flights_bp.route('/flights/<int:flight_id>/subscribe', methods=['POST'])
@jwt_required()
@swag_from({
    'responses': {
        201: {
            'description': 'Subscribed to flight successfully',
            'examples': {
                'application/json': {
                    'message': 'Subscribed to flight successfully'
                }
            }
        },
        400: {
            'description': 'User already subscribed to this flight',
            'examples': {
                'application/json': {
                    'message': 'User already subscribed to this flight'
                }
            }
        },
        404: {
            'description': 'User or Flight not found',
            'examples': {
                'application/json': {
                    'message': 'User not found'
                },
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
def subscribe_to_flight(flight_id):
    """
    Subscribe a user to notifications for a specific flight.
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    flight = Flight.query.get(flight_id)

    if not user:
        return jsonify({"message": "User not found"}), 404
    if not flight:
        return jsonify({"message": "Flight not found"}), 404

    # Check if the user is already subscribed to this flight
    existing_subscription = FlightSubscription.query.filter_by(user_id=user_id, flight_id=flight_id).first()
    if existing_subscription:
        return jsonify({"message": "User already subscribed to this flight"}), 400
    
    # Create a new subscription
    subscription = FlightSubscription(user_id=user_id, flight_id=flight_id)
    db.session.add(subscription)
    db.session.commit()
    
    return jsonify({"message": "Subscribed to flight successfully"}), 201

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Flight, db, FlightSubscription, User
from app.services.flight_service import fetch_flight_data

# Create a Blueprint for flight routes
flights_bp = Blueprint('flights', __name__)

@flights_bp.route('/flights', methods=['GET'])
@jwt_required()
def get_flights():
    """
    Fetch real-time flight data from the external API.
    """
    flight_number = request.args.get('flight_number')
    date = request.args.get('date')  # Optional: Specify a date for the flight data

    # Fetch flight data from the external API
    flights = fetch_flight_data(flight_number=flight_number, date=date)

    if not flights:
        return jsonify({"message": "No flight data found"}), 404

    return jsonify({"data": flights}), 200


@flights_bp.route('/flights/<int:flight_id>', methods=['GET'])
@jwt_required()
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
def subscribe_to_flight(flight_id):
    """
    Subscribe a user to notifications for a specific flight.
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    flight = Flight.query.get(flight_id)
    if not user:
       return jsonify({"message": "User not found"}), 4
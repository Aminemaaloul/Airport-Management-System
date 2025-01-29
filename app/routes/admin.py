from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models import Flight, User, Notification, Baggage, db
from decorators import admin_required
from datetime import datetime
from app.services.notifications import send_notification

# Create a Blueprint for admin routes
admin_bp = Blueprint('admin', __name__)

# Admin endpoint to add a new flight
@admin_bp.route('/admin/flights', methods=['POST'])
@jwt_required()
@admin_required
def add_flight():
    """
    Add a new flight (Admin only).
    """
    data = request.get_json()
    flight = Flight(
        flight_number=data['flight_number'],
        departure_airport=data['departure_airport'],
        arrival_airport=data['arrival_airport'],
        departure_time=data['departure_time'],
        arrival_time=data['arrival_time'],
        status=data.get('status', 'scheduled'),
        airline=data.get('airline', 'Unknown')
    )
    db.session.add(flight)
    db.session.commit()
    return jsonify({"message": "Flight added successfully", "data": flight.serialize()}), 201

# Admin endpoint to update flight status
@admin_bp.route('/admin/flights/<int:flight_id>', methods=['PUT'])
@jwt_required()
@admin_required
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

# Admin endpoint to delete a flight
@admin_bp.route('/admin/flights/<int:flight_id>', methods=['DELETE'])
@jwt_required()
@admin_required
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

# Admin endpoint to fetch all users
@admin_bp.route('/admin/users', methods=['GET'])
@jwt_required()
@admin_required
def get_all_users():
    """
    Fetch all users (Admin only).
    """
    users = User.query.all()
    return jsonify({"data": [user.serialize() for user in users]}), 200

# Admin endpoint to delete a user
@admin_bp.route('/admin/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
@admin_required
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

# Admin endpoint to send a notification to all users
@admin_bp.route('/admin/notifications', methods=['POST'])
@jwt_required()
@admin_required
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

# Admin endpoint to notify passengers about flight updates
@admin_bp.route('/admin/flights/<int:flight_id>/notify', methods=['POST'])
@jwt_required()
@admin_required
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

# Admin endpoint to send a baggage alert
@admin_bp.route('/admin/baggage/alert', methods=['POST'])
@jwt_required()
@admin_required
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
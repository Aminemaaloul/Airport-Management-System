from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import ParkingSpot, db, ParkingReservation, User
from decorators import admin_required
from datetime import datetime

parking_bp = Blueprint('parking', __name__)

@parking_bp.route('/parking/availability', methods=['GET'])
@jwt_required()
def check_parking_availability():
    """
    Check available parking spots.
    """
    parking_spots = ParkingSpot.query.filter_by(status='available').all()
    return jsonify({"data": [spot.serialize() for spot in parking_spots]}), 200

@parking_bp.route('/parking/reserve', methods=['POST'])
@jwt_required()
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

@parking_bp.route('/admin/parking', methods=['GET'])
@jwt_required()
@admin_required
def get_all_parking_spots():
    """
    Get all parking spots.
    """
    parking_spots = ParkingSpot.query.all()
    return jsonify({"data": [spot.serialize() for spot in parking_spots]}), 200

@parking_bp.route('/admin/parking/<int:spot_id>', methods=['PUT'])
@jwt_required()
@admin_required
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

@parking_bp.route('/users/me/parking', methods=['GET'])
@jwt_required()
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
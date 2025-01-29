from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Baggage, db, User
from decorators import admin_required

baggage_bp = Blueprint('baggage', __name__)

@baggage_bp.route('/baggage/track', methods=['GET'])
@jwt_required()
def track_baggage():
    """
    Track baggage status.
    """
    baggage_tag = request.args.get('baggage_tag')
    baggage = Baggage.query.filter_by(baggage_tag=baggage_tag).first()
    if not baggage:
        return jsonify({"message": "Baggage not found"}), 404
    return jsonify({"data":baggage.serialize()}), 200

@baggage_bp.route('/users/me/baggage', methods=['GET'])
@jwt_required()
def get_user_baggage():
    """
    Retrieve baggage status for a specific user.
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    baggages = Baggage.query.filter(Baggage.flight.has(subscriptions=any(user_id=user_id))).all()
    return jsonify({"data":[baggage.serialize() for baggage in baggages]}), 200


@baggage_bp.route('/admin/baggage/<int:flight_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_flight_baggage(flight_id):
    """
     Retrieve all baggage associated with a specific flight.
    """
    baggage = Baggage.query.filter_by(flight_id=flight_id).all()
    return jsonify({"data": [bag.serialize() for bag in baggage]}), 200


@baggage_bp.route('/admin/baggage/<int:baggage_id>', methods=['PUT'])
@jwt_required()
@admin_required
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
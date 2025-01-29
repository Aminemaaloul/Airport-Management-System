from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import AssistanceRequest, db
from datetime import datetime
from decorators import admin_required

assistance_bp = Blueprint('assistance', __name__)

@assistance_bp.route('/assistance', methods=['POST'])
@jwt_required()
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
def get_assistance_status():
    """
    Get the status of an assistance request.
    """
    user_id = get_jwt_identity()
    assistance_request = AssistanceRequest.query.filter_by(user_id=user_id).first()
    if not assistance_request:
        return jsonify({"message": "No assistance request found"}), 404
    return jsonify({"data": assistance_request.serialize()}), 200

@assistance_bp.route('/admin/assistance', methods=['GET'])
@jwt_required()
@admin_required
def get_all_assistance_requests():
    """
    Get all assistance requests.
    """
    assistance_requests = AssistanceRequest.query.all()
    return jsonify({"data": [request.serialize() for request in assistance_requests]}), 200

@assistance_bp.route('/admin/assistance/<int:request_id>', methods=['PUT'])
@jwt_required()
@admin_required
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

@assistance_bp.route('/admin/assistance/<int:request_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_assistance_request(request_id):
    """
    Delete assistance request.
    """
    assistance_request = AssistanceRequest.query.get(request_id)
    if not assistance_request:
        return jsonify({"message": "Assistance request not found"}), 404
    
    db.session.delete(assistance_request)
    db.session.commit()
    return jsonify({"message": "Assistance request deleted"}), 200
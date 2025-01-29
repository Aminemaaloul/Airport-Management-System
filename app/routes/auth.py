from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from app.models import User, db
from werkzeug.security import generate_password_hash, check_password_hash

# Create a Blueprint for authentication routes
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/users/register', methods=['POST'])
def register():
    """
    Register a new user.
    """
    data = request.get_json()

    # Validate input
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({"message": "Missing required fields"}), 400

    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"message": "User already exists"}), 400

    # Hash the password
    hashed_password = generate_password_hash(data['password'])

    # Create the user
    user = User(
        username=data['username'],
        email=data['email'],
        password=hashed_password
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered successfully", "data": user.serialize()}), 201

@auth_bp.route('/users/login', methods=['POST'])
def login():
    """
    Authenticate a user and return a JWT token.
    """
    data = request.get_json()

    # Validate input
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"message": "Missing email or password"}), 400

    # Find the user
    user = User.query.filter_by(email=data['email']).first()

    # Check password
    if user and check_password_hash(user.password, data['password']):
        access_token = create_access_token(identity=str(user.id))
        return jsonify(access_token=access_token, user=user.serialize()), 200

    return jsonify({"message": "Invalid credentials"}), 401

@auth_bp.route('/users/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Get the current authenticated user's information.
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    return jsonify({"data": user.serialize()}), 200
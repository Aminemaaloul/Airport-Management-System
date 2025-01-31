from functools import wraps
from flask_jwt_extended import get_jwt_identity
from flask import jsonify
from app.models import User

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or user.role != "admin":
            return jsonify({"message": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated_function
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import jwt
import os

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/login', methods=['POST'])
def login():
    # For now, return a simple success response
    # We'll implement proper auth later
    token = jwt.encode(
        {
            'exp': datetime.utcnow() + timedelta(days=1),
            'iat': datetime.utcnow(),
            'sub': 'temp_user'
        },
        os.getenv('JWT_SECRET_KEY'),
        algorithm='HS256'
    )
    return jsonify({"token": token})

"""
Authentication middleware for protecting routes that require authentication.
This middleware verifies the JWT token and adds the user_id to the Flask global object.
"""
from functools import wraps
from flask import request, jsonify, g
import jwt
import os
from app.utils.log import get_logger

logger = get_logger(__name__)

def token_required(f):
    """
    Decorator to ensure that a valid token is present in the request
    Adds user_id to Flask's g object for use in the route function
    
    Usage:
    @token_required
    def protected_route():
        user_id = g.user_id
        # ... rest of the route function
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            logger.warning("Token is missing")
            return jsonify({'message': 'Authentication required. Please login.', 'error': 'token_missing'}), 401
        
        try:
            # Decode the token
            secret_key = os.getenv('SECRET_KEY', 'default_secret_key')
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            g.user_id = payload['sub']  # Store user_id in Flask's g object
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return jsonify({'message': 'Token expired. Please login again.', 'error': 'token_expired'}), 401
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return jsonify({'message': 'Invalid token. Please login again.', 'error': 'token_invalid'}), 401
        
        return f(*args, **kwargs)
    
    return decorated
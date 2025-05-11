from flask import jsonify, request
from . import auth_bp
from app.services.auth_service import AuthService
from functools import wraps
from app.utils.log import get_logger

logger = get_logger(__name__)

def token_required(f):
    """
    Decorator to ensure that a valid token is present in the request
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            logger.warning("Token is missing")
            return jsonify({'message': 'Token is missing'}), 401
        
        result = AuthService.verify_token(token)
        if isinstance(result, tuple) and result[0] is None:
            logger.warning(f"Token verification failed: {result[1]}")
            return jsonify({'message': result[1]}), 401
        
        # result is user_id if valid
        request.user_id = result
        return f(*args, **kwargs)
    
    return decorated


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user
    """
    data = request.get_json()
    
    # Validate request data
    required_fields = ['first_name', 'last_name', 'email', 'username', 'password']
    for field in required_fields:
        if field not in data:
            logger.warning(f"Registration failed: Missing {field}")
            return jsonify({'message': f'Missing {field}'}), 400
    
    # Register user
    user_id, message = AuthService.register(
        data['first_name'],
        data['last_name'],
        data['email'],
        data['username'],
        data['password']
    )
    
    if user_id:
        return jsonify({
            'message': message,
            'user_id': user_id
        }), 201
    else:
        return jsonify({'message': message}), 400


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login a user
    """
    data = request.get_json()
    
    # Validate request data
    if not data or not data.get('username') or not data.get('password'):
        logger.warning("Login failed: Missing username or password")
        return jsonify({'message': 'Missing username or password'}), 400
    
    # Login user
    result, message = AuthService.login(
        data['username'],
        data['password']
    )
    
    if result:
        return jsonify({
            'message': message,
            'data': result
        }), 200
    else:
        return jsonify({'message': message}), 401


@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile():
    """
    Get user profile
    """
    user_id = request.user_id
    
    # Get profile
    profile, message = AuthService.get_profile(user_id)
    
    if profile:
        return jsonify({
            'message': message,
            'data': profile
        }), 200
    else:
        return jsonify({'message': message}), 404


@auth_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile():
    """
    Update user profile
    """
    user_id = request.user_id
    data = request.get_json()
    
    # Update profile
    success, message = AuthService.update_profile(user_id, data)
    
    if success:
        return jsonify({'message': message}), 200
    else:
        return jsonify({'message': message}), 400

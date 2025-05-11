# DEPRECATED: Please use app/api/auth/services.py instead
# This file is kept for reference and backward compatibility

import jwt
import datetime
import os
from app.api.auth.models import Auth, Profile  # Updated import path
from app.utils.log import get_logger

logger = get_logger(__name__)

class AuthService:
    """
    Authentication service for handling user authentication operations
    """
    
    @staticmethod
    def register(first_name, last_name, email, username, password):
        """
        Register a new user
        """
        # Check if user exists
        if Auth.get_user_by_email(email):
            logger.warning(f"Registration failed: Email {email} already exists")
            return None, "Email already exists"
        
        if Auth.get_user_by_username(username):
            logger.warning(f"Registration failed: Username {username} already exists")
            return None, "Username already exists"
        
        try:
            # Create user
            user_id = Auth.create_user(first_name, last_name, email, username, password)
            
            # Create profile
            Profile.create_profile(user_id)
            
            logger.info(f"User registered successfully: {username}")
            return user_id, "User registered successfully"
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return None, f"Registration error: {str(e)}"
    
    @staticmethod
    def login(username, password):
        """
        Login a user
        """
        try:
            # Get user
            user = Auth.get_user_by_username(username)
            
            # Check if user exists and password is correct
            if not user or not Auth.check_password(user, password):
                logger.warning(f"Login failed: Invalid credentials for {username}")
                return None, "Invalid username or password"
            
            # Generate token
            token = AuthService.generate_token(user['user_id'])
            
            logger.info(f"User logged in successfully: {username}")
            return {
                'token': token,
                'user_id': user['user_id'],
                'username': user['username'],
                'email': user['email'],
                'first_name': user['first_name'],
                'last_name': user['last_name']
            }, "Login successful"
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return None, f"Login error: {str(e)}"
    
    @staticmethod
    def generate_token(user_id):
        """
        Generate JWT token
        """
        secret_key = os.getenv('SECRET_KEY', 'default_secret_key')
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
            'iat': datetime.datetime.utcnow(),
            'sub': user_id
        }
        return jwt.encode(payload, secret_key, algorithm='HS256')
    
    @staticmethod
    def verify_token(token):
        """
        Verify JWT token
        """
        try:
            secret_key = os.getenv('SECRET_KEY', 'default_secret_key')
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            return payload['sub']  # Return user_id
        except jwt.ExpiredSignatureError:
            return None, "Token expired. Please login again."
        except jwt.InvalidTokenError:
            return None, "Invalid token. Please login again."
    
    @staticmethod
    def get_profile(user_id):
        """
        Get user profile
        """
        try:
            # Get user
            user = Auth.get_user_by_id(user_id)
            if not user:
                logger.warning(f"Profile retrieval failed: User {user_id} not found")
                return None, "User not found"
            
            # Get profile
            profile = Profile.get_profile_by_user_id(user_id)
            if not profile:
                logger.warning(f"Profile retrieval failed: Profile for user {user_id} not found")
                return None, "Profile not found"
            
            # Combine user and profile data
            user_data = {
                'user_id': user['user_id'],
                'username': user['username'],
                'email': user['email'],
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'avatar': profile.get('avatar'),
                'cover_image': profile.get('cover_image'),
                'description': profile.get('description'),
            }
            
            logger.info(f"Profile retrieved successfully for user: {user['username']}")
            return user_data, "Profile retrieved successfully"
        except Exception as e:
            logger.error(f"Profile retrieval error: {str(e)}")
            return None, f"Profile retrieval error: {str(e)}"
    
    @staticmethod
    def update_profile(user_id, profile_data):
        """
        Update user profile
        """
        try:
            # Check if user exists
            user = Auth.get_user_by_id(user_id)
            if not user:
                logger.warning(f"Profile update failed: User {user_id} not found")
                return False, "User not found"
            
            # Check if profile exists
            profile = Profile.get_profile_by_user_id(user_id)
            if not profile:
                logger.warning(f"Profile update failed: Profile for user {user_id} not found")
                return False, "Profile not found"
            
            # Separate user and profile data
            user_data = {}
            profile_data_filtered = {}
            
            # Fields that belong to auth model
            auth_fields = ['first_name', 'last_name', 'email']
            
            # Fields that belong to profile model
            profile_fields = ['avatar', 'cover_image', 'description']
            
            # Filter data
            for key, value in profile_data.items():
                if key in auth_fields:
                    user_data[key] = value
                elif key in profile_fields:
                    profile_data_filtered[key] = value
            
            # Update user if there's user data to update
            if user_data:
                Auth.update_user(user_id, user_data)
            
            # Update profile if there's profile data to update
            if profile_data_filtered:
                Profile.update_profile(user_id, profile_data_filtered)
            
            logger.info(f"Profile updated successfully for user: {user['username']}")
            return True, "Profile updated successfully"
        except Exception as e:
            logger.error(f"Profile update error: {str(e)}")
            return False, f"Profile update error: {str(e)}"

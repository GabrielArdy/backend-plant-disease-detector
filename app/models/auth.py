# DEPRECATED: Please use app/api/auth/models.py instead
# This file is kept for reference and backward compatibility

from datetime import datetime
import uuid
from app.extensions import mongo, bcrypt
from bson.objectid import ObjectId

class Auth:
    """
    Auth model for user authentication
    """
    @staticmethod
    def create_user(first_name, last_name, email, username, password):
        """
        Create a new user
        """
        user_id = str(uuid.uuid4())
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        user = {
            'user_id': user_id,
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'username': username,
            'password': hashed_password,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        mongo.db.auth.insert_one(user)
        return user_id
    
    @staticmethod
    def get_user_by_username(username):
        """
        Get user by username
        """
        return mongo.db.auth.find_one({'username': username})
    
    @staticmethod
    def get_user_by_email(email):
        """
        Get user by email
        """
        return mongo.db.auth.find_one({'email': email})
    
    @staticmethod
    def get_user_by_id(user_id):
        """
        Get user by ID
        """
        return mongo.db.auth.find_one({'user_id': user_id})
    
    @staticmethod
    def check_password(user, password):
        """
        Check if password is correct
        """
        if user and bcrypt.check_password_hash(user['password'], password):
            return True
        return False
    
    @staticmethod
    def update_user(user_id, update_data):
        """
        Update user data
        """
        update_data['updated_at'] = datetime.utcnow()
        
        # Don't allow updating of sensitive fields
        for field in ['user_id', 'password', 'created_at']:
            if field in update_data:
                del update_data[field]
        
        mongo.db.auth.update_one(
            {'user_id': user_id},
            {'$set': update_data}
        )
        
    @staticmethod
    def change_password(user_id, new_password):
        """
        Change user password
        """
        hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        
        mongo.db.auth.update_one(
            {'user_id': user_id},
            {
                '$set': {
                    'password': hashed_password,
                    'updated_at': datetime.utcnow()
                }
            }
        )


class Profile:
    """
    Profile model for user profile information
    """
    @staticmethod
    def create_profile(user_id, avatar=None, cover_image=None, description=None):
        """
        Create a new user profile
        """
        profile = {
            'user_id': user_id,
            'avatar': avatar,
            'cover_image': cover_image,
            'description': description,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        mongo.db.profile.insert_one(profile)
        return user_id
    
    @staticmethod
    def get_profile_by_user_id(user_id):
        """
        Get profile by user ID
        """
        return mongo.db.profile.find_one({'user_id': user_id})
    
    @staticmethod
    def update_profile(user_id, update_data):
        """
        Update profile data
        """
        update_data['updated_at'] = datetime.utcnow()
        
        # Don't allow updating of sensitive fields
        for field in ['user_id', 'created_at']:
            if field in update_data:
                del update_data[field]
        
        mongo.db.profile.update_one(
            {'user_id': user_id},
            {'$set': update_data}
        )

from app.models.auth import Auth, Profile
from app.utils.log import get_logger

logger = get_logger(__name__)

class AuthService:
    """
    Authentication service for the auth blueprint
    """
    @staticmethod
    def register_user(first_name, last_name, email, username, password):
        """
        Register a new user
        """
        return Auth.create_user(first_name, last_name, email, username, password)
    
    @staticmethod
    def verify_credentials(username, password):
        """
        Verify user credentials
        """
        user = Auth.get_user_by_username(username)
        if user and Auth.check_password(user, password):
            return user
        return None

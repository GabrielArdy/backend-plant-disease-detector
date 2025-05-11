from app.extensions import mongo, bcrypt
from app.utils.log import get_logger
import uuid
from datetime import datetime
import os

logger = get_logger(__name__)

def init_mongo_collections():
    """
    Initialize MongoDB collections with indexes
    """
    try:
        # Create indexes for auth collection
        mongo.db.auth.create_index('user_id', unique=True)
        mongo.db.auth.create_index('email', unique=True)
        mongo.db.auth.create_index('username', unique=True)
        
        # Create indexes for profile collection
        mongo.db.profile.create_index('user_id', unique=True)
        
        # Create indexes for prediction_history collection
        mongo.db.prediction_history.create_index('prediction_id', unique=True)
        mongo.db.prediction_history.create_index('user_id')  # Non-unique index for faster queries
        mongo.db.prediction_history.create_index('timestamp')  # For sorting by date
        
        # Create demo user if in development mode
        if os.getenv('FLASK_ENV') == 'development':
            create_demo_user()
        
        logger.info("MongoDB collections initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing MongoDB collections: {str(e)}")

def create_demo_user():
    """
    Create a demo user for development purposes
    """
    try:
        # Check if demo user already exists
        if mongo.db.auth.find_one({'username': 'demo'}):
            logger.info("Demo user already exists")
            return
            
        # Create demo user
        user_id = str(uuid.uuid4())
        hashed_password = bcrypt.generate_password_hash('demo123').decode('utf-8')
        
        user = {
            'user_id': user_id,
            'first_name': 'Demo',
            'last_name': 'User',
            'email': 'demo@example.com',
            'username': 'demo',
            'password': hashed_password,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        mongo.db.auth.insert_one(user)
        
        # Create demo user profile
        profile = {
            'user_id': user_id,
            'avatar': 'https://randomuser.me/api/portraits/men/22.jpg',
            'cover_image': 'https://picsum.photos/800/200',
            'description': 'This is a demo user profile for testing purposes',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        mongo.db.profile.insert_one(profile)
        
        logger.info("Demo user created successfully")
    except Exception as e:
        logger.error(f"Error creating demo user: {str(e)}")

from flask import Flask, current_app, g
from flask_cors import CORS
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from gridfs import GridFS
from pymongo import MongoClient
from functools import wraps
import logging
import threading

# Get logger
logger = logging.getLogger(__name__)

# Initialize extensions
mongo = PyMongo()
bcrypt = Bcrypt()
cors = CORS()

# A thread-safe wrapper class for GridFS that ensures initialization happens
# only once per thread and only after the Flask app context is available
class GridFSProxy:
    def __init__(self):
        self._fs = None
        self._initialized = False
        self._lock = threading.RLock()  # Reentrant lock for thread safety
        
    def _ensure_initialized(self):
        """Ensure GridFS is initialized before any operation, thread-safe"""
        # Quick check without lock
        if not self._initialized:
            # Acquire lock for initialization
            with self._lock:
                # Double check after acquiring lock
                if not self._initialized:
                    try:
                        # First check if we're in an application context
                        if not current_app:
                            raise RuntimeError("No Flask application context available")
                        
                        # Check if MongoDB connection is established
                        if not hasattr(mongo, 'db') or mongo.db is None:
                            raise RuntimeError("MongoDB connection not established")
                        
                        logger.info("Initializing GridFS")
                        self._fs = GridFS(mongo.db)
                        self._initialized = True
                        logger.info("GridFS initialized successfully")
                        
                    except RuntimeError as e:
                        logger.error(f"GridFS initialization error: {str(e)}")
                        raise
                    except Exception as e:
                        logger.error(f"Unexpected error initializing GridFS: {str(e)}")
                        raise RuntimeError(f"Failed to initialize GridFS: {str(e)}")
    
    def __getattr__(self, name):
        """Forward all attribute access to the actual GridFS instance"""
        try:
            self._ensure_initialized()
            if self._fs is None:
                raise RuntimeError("GridFS could not be initialized")
            return getattr(self._fs, name)
        except Exception as e:
            logger.error(f"Error accessing GridFS.{name}: {str(e)}")
            raise
        
    def reset(self):
        """Reset the GridFS instance (mainly for testing), thread-safe"""
        with self._lock:
            self._fs = None
            self._initialized = False
        
# Create a proxy instance
fs = GridFSProxy()

def init_extensions(app: Flask):
    """Initialize Flask extensions"""
    logger.info("Initializing Flask extensions")
    mongo.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app)
    
    # Add a function to ensure each request has access to GridFS
    @app.before_request
    def ensure_gridfs_access():
        """Ensure GridFS is accessible for each request"""
        try:
            if not hasattr(fs, '_initialized') or not fs._initialized:
                _ = fs.exists("test")  # This will trigger initialization
                if not hasattr(fs, '_initialized') or not fs._initialized:
                    logger.error("GridFS could not be initialized")
        except Exception as e:
            logger.error(f"Error ensuring GridFS access: {str(e)}")
    
    # Initialize GridFS right away within the app context
    with app.app_context():
        try:
            logger.info("Initializing GridFS during app startup")
            # Reset first in case there was a prior partial initialization
            fs.reset()
            # Access an attribute to trigger initialization
            _ = fs.exists("test")
            logger.info("GridFS initialized successfully during app startup")
        except Exception as e:
            logger.error(f"Error initializing GridFS during app startup: {str(e)}")
    
    logger.info("Flask extensions initialized successfully")

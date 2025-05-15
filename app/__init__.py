from flask import Flask, jsonify
import tensorflow as tf
import os
from dotenv import load_dotenv
from pathlib import Path
from app.config import config
from app.extensions import init_extensions
from app.api.auth import auth_bp
from app.api.prediction import prediction_bp
from app.utils.log import get_logger
from app.utils.gpu_utils import setup_gpu
from app.db import init_mongo_collections

# Initialize logger
logger = get_logger(__name__)

# Load environment variables from local.env file
env_path = Path(__file__).parent.parent / 'local.env'
if env_path.exists():
    logger.info(f"Loading environment variables from {env_path}")
    load_dotenv(dotenv_path=env_path)
else:
    logger.warning(f"Environment file {env_path} not found. Using default variables.")

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Check for GPU availability and configure TensorFlow
    using_gpu = setup_gpu()
    logger.info(f"TensorFlow configured to use {'GPU' if using_gpu else 'CPU'}")

    # Initialize extensions
    init_extensions(app)
    
    # Initialize MongoDB collections
    with app.app_context():
        init_mongo_collections()
        
    # Check Gemini AI connection status
    try:
        from app.services.advice_service import check_gemini_connection
        
        genai_status = check_gemini_connection()
        if genai_status['available']:
            if 'error' in genai_status and genai_status['error']:
                logger.warning(f"Gemini AI warning: {genai_status['error']}")
            else:
                model_details = genai_status.get('model_details', {})
                model_name = model_details.get('display_name', genai_status['model_name'])
                logger.info(f"Connected to Gemini AI service. Model: {model_name}")
        else:
            error = genai_status.get('error', 'Unknown error')
            logger.warning(f"Gemini AI service not available: {error}")
    except Exception as e:
        logger.error(f"Error checking Gemini connection: {str(e)}")

    # Register blueprints
    app.register_blueprint(prediction_bp)
    app.register_blueprint(auth_bp)
    
    # Register the health blueprint
    from app.api.health import health_bp
    app.register_blueprint(health_bp)

    logger.info(f"Application created with {config_name} configuration")
    return app

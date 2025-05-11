from flask import Flask, jsonify
from app.config import config
from app.extensions import init_extensions
from app.api.auth import auth_bp
from app.api.prediction import prediction_bp
from app.utils.log import get_logger
from app.db import init_mongo_collections

# Initialize logger
logger = get_logger(__name__)

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    init_extensions(app)
    
    # Initialize MongoDB collections
    with app.app_context():
        init_mongo_collections()

    # Register blueprints
    app.register_blueprint(prediction_bp)
    app.register_blueprint(auth_bp)

    # Add health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """
        Health check endpoint to verify the API is running
        """
        return jsonify({
            'status': 'ok',
            'message': 'Plant Disease API is running',
            'version': '1.0.0',
            'environment': config_name
        })

    logger.info(f"Application created with {config_name} configuration")
    return app

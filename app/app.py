from flask import Flask
from controllers.prediction_controller import prediction_bp
from utils.log import get_logger

# Initialize logger
logger = get_logger(__name__)

# Create Flask application
app = Flask(__name__)

# Register blueprints
app.register_blueprint(prediction_bp)

if __name__ == '__main__':
    # Set host to '0.0.0.0' to make the server publicly available
    # Set port to 5000 (or any other port you prefer)
    app.run(host='0.0.0.0', port=5000, debug=True)
    logger.info("Starting Flask application...")
    logger.info("Flask application started successfully.")
    logger.info("Listening on port 5000...")

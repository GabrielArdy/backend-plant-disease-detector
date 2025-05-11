from app import create_app
import os
from app.utils.log import get_logger

logger = get_logger(__name__)

# Get environment from environment variable, default to development
env = os.getenv('FLASK_ENV', 'development')
app = create_app(env)

if __name__ == '__main__':
    logger.info(f"Starting application in {env} mode")
    app.run(host='0.0.0.0', port=5000)

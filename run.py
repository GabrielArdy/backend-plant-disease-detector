from app import create_app
import os
from app.utils.log import get_logger

logger = get_logger(__name__)

# Get environment from environment variable, default to development
env = os.getenv('FLASK_ENV', 'development')
app = create_app(env)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = env == 'development'
    
    logger.info(f"Starting application in {env} mode on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)

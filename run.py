import os
from pathlib import Path
from dotenv import load_dotenv
from app.utils.log import get_logger

# Initialize logger
logger = get_logger(__name__)

# Load environment variables from local.env file
env_path = Path(__file__).parent / 'local.env'
if env_path.exists():
    logger.info(f"Loading environment variables from {env_path}")
    load_dotenv(dotenv_path=env_path)
else:
    logger.warning(f"Environment file {env_path} not found. Using default variables.")

from app import create_app

# Get environment from environment variable, default to development
env = os.getenv('FLASK_ENV', 'development')
app = create_app(env)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = env == 'development'
    
    logger.info(f"Starting application in {env} mode on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)

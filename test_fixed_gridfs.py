"""
Test script to verify the fixed GridFS implementation
"""
from flask import Flask
import os
from pathlib import Path
from dotenv import load_dotenv
from app import create_app
from app.extensions import fs
from app.utils.log import get_logger
import io
from PIL import Image

# Initialize logger
logger = get_logger(__name__)

# Load environment variables
env_path = Path(__file__).parent / 'local.env'
if env_path.exists():
    logger.info(f"Loading environment variables from {env_path}")
    load_dotenv(dotenv_path=env_path)
else:
    logger.warning(f"Environment file {env_path} not found. Using default variables.")

def test_gridfs():
    """Test the fixed GridFS implementation"""
    app = create_app('development')
    
    with app.app_context():
        try:
            logger.info("Testing GridFS implementation...")
            
            # Create test image
            logger.info("Creating test image...")
            img = Image.new('RGB', (100, 100), color='red')
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='JPEG')
            img_bytes.seek(0)
            
            # Save to GridFS
            logger.info("Saving to GridFS...")
            file_id = fs.put(img_bytes.read(), filename='test_fixed.jpg', content_type='image/jpeg')
            logger.info(f"Image saved with ID: {file_id}")
            
            # Get from GridFS
            logger.info("Getting from GridFS...")
            retrieved = fs.get(file_id)
            logger.info(f"Retrieved image: {retrieved.filename}, {retrieved.content_type}")
            
            # Clean up
            logger.info("Cleaning up...")
            fs.delete(file_id)
            
            logger.info("GridFS test passed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"GridFS test failed: {str(e)}")
            return False

if __name__ == "__main__":
    success = test_gridfs()
    print(f"GridFS test {'PASSED' if success else 'FAILED'}")

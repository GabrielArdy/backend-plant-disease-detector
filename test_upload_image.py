"""
Test script to test image upload functionality with GridFS
"""
from flask import Flask
from app import create_app
from app.utils.storage import ImageStorage
from app.utils.log import get_logger
import io
from PIL import Image
import uuid
import sys
import logging
import sys

# Initialize logger with console output
logger = get_logger(__name__)
# Add console handler to ensure we see the logs
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)

def test_image_upload():
    """Test the ImageStorage class's save_prediction_image function"""
    # Create a test Flask app
    app = create_app('development')
    
    with app.app_context():
        try:
            logger.info("Testing image upload with GridFS...")
            
            # Create test image
            logger.info("Creating test image...")
            img = Image.new('RGB', (300, 300), color='blue')
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='JPEG')
            img_bytes.seek(0)
            
            # Generate a fake prediction ID
            prediction_id = str(uuid.uuid4())
            logger.info(f"Using prediction ID: {prediction_id}")
            
            # Test the ImageStorage class
            logger.info("Saving image using ImageStorage...")
            file_id = ImageStorage.save_prediction_image(img_bytes, prediction_id, "test_user")
            
            if file_id:
                logger.info(f"Image saved successfully with ID: {file_id}")
                
                # Verify we can retrieve it
                logger.info("Testing image retrieval...")
                retrieved_data = ImageStorage.get_image_from_gridfs(file_id)
                if retrieved_data:
                    logger.info(f"Retrieved image successfully: {len(retrieved_data)} bytes")
                    
                    # Test metadata retrieval
                    logger.info("Testing metadata retrieval...")
                    metadata = ImageStorage.get_image_metadata(file_id)
                    if metadata:
                        logger.info(f"Metadata retrieved successfully:")
                        logger.info(f"  - Content type: {metadata.get('content_type')}")
                        logger.info(f"  - Prediction ID: {metadata.get('prediction_id')}")
                        logger.info(f"  - User ID: {metadata.get('user_id')}")
                    else:
                        logger.error("Failed to retrieve metadata")
                        
                    # Clean up
                    logger.info("Deleting test image...")
                    ImageStorage.delete_image(file_id)
                    logger.info("Image deleted successfully")
                    return True
                else:
                    logger.error("Failed to retrieve image")
            else:
                logger.error("Failed to save image")
                
            return False
            
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return False

if __name__ == "__main__":
    success = test_image_upload()
    print(f"Image upload test {'PASSED' if success else 'FAILED'}")

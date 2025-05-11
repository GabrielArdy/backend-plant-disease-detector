import os
import uuid
import base64
from datetime import datetime
from PIL import Image
from io import BytesIO
from app.utils.log import get_logger

logger = get_logger(__name__)

class ImageStorage:
    """Utility class for handling image storage operations"""
    
    # Base directory for storing uploaded images
    BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'uploads')
    
    @classmethod
    def save_prediction_image(cls, image_file, prediction_id, user_id='anonymous'):
        """
        Save an uploaded image for a prediction
        
        Args:
            image_file: The uploaded image file object
            prediction_id: ID of the prediction
            user_id: ID of the user who uploaded the image
            
        Returns:
            str: Path to the saved image, relative to the uploads directory
        """
        try:
            # Create directories if they don't exist
            year_month = datetime.now().strftime('%Y-%m')
            directory = os.path.join(cls.BASE_DIR, year_month)
            
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                
            # Generate filename
            filename = f"{prediction_id}.jpg"
            filepath = os.path.join(directory, filename)
            
            # Reset file pointer to beginning
            image_file.seek(0)
            
            # Open and save as JPEG
            img = Image.open(image_file)
            img.save(filepath, "JPEG", quality=85)
            
            # Return relative path
            relative_path = os.path.join(year_month, filename)
            logger.info(f"Image saved at {relative_path}")
            
            return relative_path
            
        except Exception as e:
            logger.error(f"Failed to save image: {str(e)}")
            return None
    
    @classmethod
    def get_image_path(cls, relative_path):
        """
        Get the absolute path of a stored image
        
        Args:
            relative_path: Path relative to the uploads directory
            
        Returns:
            str: Absolute path to the image
        """
        if not relative_path:
            return None
            
        return os.path.join(cls.BASE_DIR, relative_path)
    
    @classmethod
    def get_image_as_base64(cls, relative_path):
        """
        Get an image as base64 encoded string
        
        Args:
            relative_path: Path relative to the uploads directory
            
        Returns:
            str: Base64 encoded image or None if not found
        """
        try:
            image_path = cls.get_image_path(relative_path)
            
            if not image_path or not os.path.exists(image_path):
                logger.warning(f"Image not found at {relative_path}")
                return None
                
            with open(image_path, "rb") as img_file:
                encoded_string = base64.b64encode(img_file.read()).decode('utf-8')
                return encoded_string
                
        except Exception as e:
            logger.error(f"Failed to get image as base64: {str(e)}")
            return None

import os
import uuid
import base64
from datetime import datetime
from PIL import Image
from io import BytesIO
from app.utils.log import get_logger
from app.extensions import fs, mongo
from bson.objectid import ObjectId
from flask import current_app

logger = get_logger(__name__)

class ImageStorage:
    """Utility class for handling image storage operations using GridFS"""
    
    # Legacy base directory for backward compatibility
    BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'uploads')
    
    @classmethod
    def save_prediction_image(cls, image_file, prediction_id, user_id='anonymous'):
        """
        Save an uploaded image for a prediction to GridFS
        
        Args:
            image_file: The uploaded image file object
            prediction_id: ID of the prediction
            user_id: ID of the user who uploaded the image
            
        Returns:
            str: GridFS file ID as string
        """
        try:
            from flask import current_app
            
            # Check if we're in application context
            if not current_app:
                logger.error("No Flask application context available")
                raise RuntimeError("No Flask application context available")
                
            # Check if GridFS is available
            if not fs:
                logger.error("GridFS instance is not available")
                raise RuntimeError("GridFS instance is not available")
                
            # Validate input parameters
            if not image_file:
                logger.error("No image file provided")
                return None
                
            if not prediction_id:
                logger.error("No prediction ID provided")
                return None
                
            # Reset file pointer to beginning
            image_file.seek(0)
            
            # Open image with PIL to convert it to JPEG
            img = Image.open(image_file)
            
            # Save image to a BytesIO object
            output = BytesIO()
            img.save(output, format="JPEG", quality=85)
            output.seek(0)
            
            # Prepare metadata
            metadata = {
                'content_type': 'image/jpeg',
                'prediction_id': prediction_id,
                'user_id': user_id,
                'timestamp': datetime.utcnow(),
                'filename': f"{prediction_id}.jpg"
            }
            
            logger.debug(f"Attempting to save image to GridFS with metadata: {metadata}")
            
            # Save to GridFS
            image_data = output.read()
            if not image_data:
                logger.error("Generated empty image data")
                return None
                
            file_id = fs.put(image_data, **metadata)
            
            logger.info(f"Image saved in GridFS with ID {file_id}")
            
            return str(file_id)
            
        except AttributeError as e:
            logger.error(f"GridFS AttributeError: {str(e)}")
            logger.error("This usually indicates that GridFS is not properly initialized")
            return None
        except Exception as e:
            logger.error(f"Failed to save image to GridFS: {str(e)}")
            return None
    
    @classmethod
    def get_image_from_gridfs(cls, file_id):
        """
        Get an image file from GridFS
        
        Args:
            file_id: GridFS file ID as string
            
        Returns:
            bytes: Image data as bytes
        """
        try:
            if not file_id:
                return None
                
            # Convert string ID to ObjectId
            obj_id = ObjectId(file_id)
            
            # Get file from GridFS
            if not fs.exists(obj_id):
                logger.warning(f"Image not found in GridFS with ID {file_id}")
                return None
                
            grid_out = fs.get(obj_id)
            return grid_out.read()
                
        except Exception as e:
            logger.error(f"Failed to get image from GridFS: {str(e)}")
            return None
            
    @classmethod
    def get_image_metadata(cls, file_id):
        """
        Get metadata for an image stored in GridFS
        
        Args:
            file_id: GridFS file ID as string
            
        Returns:
            dict: Image metadata
        """
        try:
            if not file_id:
                return None
                
            # Convert string ID to ObjectId
            obj_id = ObjectId(file_id)
            
            # Get the GridFS file directly - this also returns metadata
            if not fs.exists(obj_id):
                logger.warning(f"Image not found in GridFS with ID {file_id}")
                return None
                
            # Get the file from GridFS
            grid_out = fs.get(obj_id)
            
            # Extract metadata from GridOut object
            metadata = {
                'content_type': grid_out.content_type,
                'filename': grid_out.filename,
                'upload_date': grid_out.upload_date,
                'length': grid_out.length
            }
            
            # Add any custom metadata
            for key in ['prediction_id', 'user_id', 'timestamp']:
                if hasattr(grid_out, key):
                    metadata[key] = getattr(grid_out, key)
                    
            return metadata
                
        except Exception as e:
            logger.error(f"Failed to get image metadata: {str(e)}")
            return None
    
    @classmethod
    def get_image_as_base64(cls, file_id):
        """
        Get an image as base64 encoded string from GridFS
        
        Args:
            file_id: GridFS file ID as string
            
        Returns:
            str: Base64 encoded image or None if not found
        """
        try:
            # For backward compatibility with file paths
            if file_id and '/' in file_id:
                # This is a path from the old storage system
                # Try to open from filesystem first
                legacy_path = os.path.join(cls.BASE_DIR, file_id)
                if os.path.exists(legacy_path):
                    with open(legacy_path, "rb") as img_file:
                        encoded_string = base64.b64encode(img_file.read()).decode('utf-8')
                        return encoded_string
            
            # Get from GridFS
            image_data = cls.get_image_from_gridfs(file_id)
            
            if not image_data:
                return None
                
            # Encode as base64
            encoded_string = base64.b64encode(image_data).decode('utf-8')
            return encoded_string
                
        except Exception as e:
            logger.error(f"Failed to get image as base64: {str(e)}")
            return None
    
    @classmethod
    def delete_image(cls, file_id):
        """
        Delete an image from GridFS
        
        Args:
            file_id: GridFS file ID as string
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            if not file_id:
                return False
                
            # Handle legacy file paths
            if '/' in file_id:
                # This is a path from the old storage system
                legacy_path = os.path.join(cls.BASE_DIR, file_id)
                if os.path.exists(legacy_path):
                    os.remove(legacy_path)
                    logger.info(f"Legacy image deleted at {legacy_path}")
                    return True
                return False
            
            # Convert string ID to ObjectId and delete from GridFS
            obj_id = ObjectId(file_id)
            
            if not fs.exists(obj_id):
                logger.warning(f"Image not found in GridFS with ID {file_id}")
                return False
                
            fs.delete(obj_id)
            logger.info(f"Image deleted from GridFS with ID {file_id}")
            return True
                
        except Exception as e:
            logger.error(f"Failed to delete image: {str(e)}")
            return False
            
    @classmethod
    def get_images_by_prediction_id(cls, prediction_id):
        """
        Get all images associated with a prediction ID
        
        Args:
            prediction_id: ID of the prediction
            
        Returns:
            list: List of file IDs for images associated with the prediction
        """
        try:
            files = mongo.db.fs.files.find({"prediction_id": prediction_id})
            return [str(file["_id"]) for file in files]
        except Exception as e:
            logger.error(f"Failed to get images for prediction: {str(e)}")
            return []
            
    @classmethod
    def get_images_by_user_id(cls, user_id):
        """
        Get all images uploaded by a specific user
        
        Args:
            user_id: ID of the user
            
        Returns:
            list: List of file IDs for images uploaded by the user
        """
        try:
            files = mongo.db.fs.files.find({"user_id": user_id})
            return [str(file["_id"]) for file in files]
        except Exception as e:
            logger.error(f"Failed to get images for user: {str(e)}")
            return []

    @classmethod
    def migrate_file_to_gridfs(cls, relative_path, prediction_id=None, user_id='anonymous'):
        """
        Migrate an existing file from the filesystem to GridFS
        
        Args:
            relative_path: Path relative to the uploads directory
            prediction_id: ID of the associated prediction
            user_id: ID of the user who uploaded the image
            
        Returns:
            str: GridFS file ID as string or None if migration failed
        """
        try:
            file_path = os.path.join(cls.BASE_DIR, relative_path)
            
            if not os.path.exists(file_path):
                logger.warning(f"File not found at {file_path}")
                return None
            
            # Extract prediction ID from filename if not provided
            if not prediction_id:
                filename = os.path.basename(relative_path)
                prediction_id = os.path.splitext(filename)[0]
            
            # Read file
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            # Prepare metadata
            metadata = {
                'content_type': 'image/jpeg',
                'prediction_id': prediction_id,
                'user_id': user_id,
                'timestamp': datetime.utcnow(),
                'filename': os.path.basename(relative_path),
                'migrated_from': relative_path
            }
            
            # Save to GridFS
            file_id = fs.put(file_data, **metadata)
            
            logger.info(f"File migrated to GridFS with ID {file_id}")
            
            return str(file_id)
            
        except Exception as e:
            logger.error(f"Failed to migrate file to GridFS: {str(e)}")
            return None

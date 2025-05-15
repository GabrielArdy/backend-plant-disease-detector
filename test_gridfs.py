#!/usr/bin/env python
# filepath: /home/ardy/plant-disease/backend/test_gridfs.py
"""
Test script for GridFS functionality
"""
from flask import Flask
from app import create_app
from app.extensions import fs
from app.utils.log import get_logger
import io
from PIL import Image
import numpy as np

# Initialize logger
logger = get_logger(__name__)

def test_gridfs():
    """Test GridFS functionality"""
    try:
        # Create a test Flask app
        app = create_app('development')
        
        with app.app_context():
            # Create a simple test image
            logger.info("Creating test image...")
            img = Image.new('RGB', (100, 100), color='red')
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='JPEG')
            img_bytes.seek(0)
            
            # Metadata for the image
            metadata = {
                'content_type': 'image/jpeg',
                'filename': 'test_image.jpg',
                'test': True
            }
            
            # Try saving to GridFS
            logger.info("Saving image to GridFS...")
            file_id = fs.put(img_bytes.read(), **metadata)
            logger.info(f"Image saved with ID: {file_id}")
            
            # Try retrieving from GridFS
            logger.info("Retrieving image from GridFS...")
            retrieved = fs.get(file_id)
            
            # Verify metadata
            logger.info(f"Content type: {retrieved.content_type}")
            logger.info(f"Filename: {retrieved.filename}")
            logger.info(f"Test flag: {retrieved.test}")
            
            # Delete the test file
            logger.info("Deleting test image...")
            fs.delete(file_id)
            
            logger.info("GridFS test completed successfully!")
            
            return True
    except Exception as e:
        logger.error(f"GridFS test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_gridfs()
    print(f"GridFS test {'succeeded' if success else 'failed'}")

"""
Unit tests for GridFS image storage functionality
"""

import unittest
import os
import io
from PIL import Image
import numpy as np
import tempfile
from bson.objectid import ObjectId

from app import create_app
from app.utils.storage import ImageStorage

class TestGridFSStorage(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment"""
        self.app = create_app(testing=True)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Create a test image
        self.test_image_data = self._create_test_image()
        
        # Mock prediction ID for testing
        self.test_prediction_id = "test-prediction-123456"
        self.test_user_id = "test-user-123"
        
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        self.temp_file.write(self.test_image_data)
        self.temp_file.close()
        
    def tearDown(self):
        """Clean up after tests"""
        # Remove temp file
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
            
        # Clean up test data from GridFS
        from app.extensions import fs, mongo
        cursor = mongo.db.fs.files.find({"prediction_id": self.test_prediction_id})
        for file_doc in cursor:
            fs.delete(file_doc["_id"])
            
        self.app_context.pop()
    
    def _create_test_image(self):
        """Create a simple test image"""
        img = Image.new('RGB', (100, 100), color='red')
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        return img_byte_arr.getvalue()
    
    def test_save_image_to_gridfs(self):
        """Test saving an image to GridFS"""
        with open(self.temp_file.name, 'rb') as f:
            # Create a file-like object for testing
            file_obj = io.BytesIO(f.read())
            
            # Save to GridFS
            file_id = ImageStorage.save_prediction_image(
                file_obj, 
                self.test_prediction_id,
                self.test_user_id
            )
            
            # Verify file was saved
            self.assertIsNotNone(file_id)
            self.assertTrue(len(file_id) > 0)
            
            # Check if the ID is a valid ObjectId string
            try:
                obj_id = ObjectId(file_id)
                self.assertEqual(str(obj_id), file_id)
            except Exception:
                self.fail("file_id is not a valid ObjectId string")
    
    def test_get_image_from_gridfs(self):
        """Test retrieving an image from GridFS"""
        # First save an image
        with open(self.temp_file.name, 'rb') as f:
            file_obj = io.BytesIO(f.read())
            file_id = ImageStorage.save_prediction_image(
                file_obj, 
                self.test_prediction_id,
                self.test_user_id
            )
        
        # Now retrieve it
        image_data = ImageStorage.get_image_from_gridfs(file_id)
        
        # Verify image was retrieved
        self.assertIsNotNone(image_data)
        self.assertTrue(len(image_data) > 0)
        
        # Verify it's a valid image
        img = Image.open(io.BytesIO(image_data))
        self.assertEqual(img.size, (100, 100))
    
    def test_get_image_metadata(self):
        """Test retrieving image metadata from GridFS"""
        # First save an image
        with open(self.temp_file.name, 'rb') as f:
            file_obj = io.BytesIO(f.read())
            file_id = ImageStorage.save_prediction_image(
                file_obj, 
                self.test_prediction_id,
                self.test_user_id
            )
        
        # Now retrieve metadata
        metadata = ImageStorage.get_image_metadata(file_id)
        
        # Verify metadata
        self.assertIsNotNone(metadata)
        self.assertEqual(metadata.get('prediction_id'), self.test_prediction_id)
        self.assertEqual(metadata.get('user_id'), self.test_user_id)
        self.assertEqual(metadata.get('filename'), f"{self.test_prediction_id}.jpg")
        self.assertEqual(metadata.get('content_type'), 'image/jpeg')
    
    def test_delete_image(self):
        """Test deleting an image from GridFS"""
        # First save an image
        with open(self.temp_file.name, 'rb') as f:
            file_obj = io.BytesIO(f.read())
            file_id = ImageStorage.save_prediction_image(
                file_obj, 
                self.test_prediction_id,
                self.test_user_id
            )
        
        # Now delete it
        result = ImageStorage.delete_image(file_id)
        
        # Verify deletion was successful
        self.assertTrue(result)
        
        # Verify it's not retrievable anymore
        image_data = ImageStorage.get_image_from_gridfs(file_id)
        self.assertIsNone(image_data)
    
    def test_get_images_by_prediction_id(self):
        """Test retrieving images by prediction ID"""
        # Save multiple images with same prediction ID
        file_ids = []
        for i in range(3):
            with open(self.temp_file.name, 'rb') as f:
                file_obj = io.BytesIO(f.read())
                file_id = ImageStorage.save_prediction_image(
                    file_obj, 
                    self.test_prediction_id,
                    self.test_user_id
                )
                file_ids.append(file_id)
        
        # Retrieve images by prediction ID
        result_ids = ImageStorage.get_images_by_prediction_id(self.test_prediction_id)
        
        # Verify all images were found
        self.assertEqual(len(result_ids), 3)
        
        # Verify all original file IDs are in the results
        for file_id in file_ids:
            self.assertIn(file_id, result_ids)

if __name__ == '__main__':
    unittest.main()

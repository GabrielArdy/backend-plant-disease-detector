#!/usr/bin/env python
# filepath: /home/ardy/plant-disease/backend/tests/test_prediction_history.py
import unittest
import os
import sys
import json
from io import BytesIO
from PIL import Image
import numpy as np
from datetime import datetime

# Add parent directory to path so we can import the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.api.prediction.models import PredictionHistory
from app.utils.generators import generate_uuid, get_current_timestamp

class TestPredictionHistory(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment before each test"""
        self.app = create_app('testing')
        self.client = self.app.test_client()
        
        # Create a test image (black square 224x224)
        img = Image.new('RGB', (224, 224), color='black')
        self.img_bytes = BytesIO()
        img.save(self.img_bytes, format='JPEG')
        self.img_bytes.seek(0)
        
        # Create a test user ID
        self.test_user_id = 'test_user_' + generate_uuid()[:8]
        
    def test_save_and_retrieve_prediction(self):
        """Test saving a prediction and retrieving it"""
        # Make a prediction
        response = self.client.post(
            '/api/prediction/predict',
            data={
                'file': (self.img_bytes, 'test_image.jpg'),
                'user_id': self.test_user_id
            },
            content_type='multipart/form-data'
        )
        
        # Check response status
        self.assertEqual(response.status_code, 200, f"Response: {response.data}")
        
        # Parse response
        result = json.loads(response.data)
        self.assertIn('prediction_id', result)
        prediction_id = result['prediction_id']
        
        # Query prediction history
        history_response = self.client.get(f'/api/prediction/history?user_id={self.test_user_id}')
        self.assertEqual(history_response.status_code, 200, f"Response: {history_response.data}")
        
        # Check that our prediction is in the history
        history_data = json.loads(history_response.data)
        self.assertIn('predictions', history_data)
        self.assertGreater(len(history_data['predictions']), 0)
        
        # Check we can get prediction by ID
        detail_response = self.client.get(f'/api/prediction/history/{prediction_id}')
        self.assertEqual(detail_response.status_code, 200, f"Response: {detail_response.data}")
        detail_data = json.loads(detail_response.data)
        self.assertEqual(detail_data['prediction_id'], prediction_id)
        
    def test_pagination(self):
        """Test that pagination works for prediction history"""
        # Create 5 test predictions
        for i in range(5):
            # Create dummy prediction data
            prediction_data = {
                'prediction_id': generate_uuid(),
                'user_id': self.test_user_id,
                'class_name': f'test_class_{i}',
                'confidence': 0.9,
                'timestamp': get_current_timestamp(),
                'plant_type': 'Test Plant',
                'condition': 'Test Disease',
                'created_at': datetime.utcnow()
            }
            
            # Save directly to database
            with self.app.app_context():
                PredictionHistory.save_prediction(prediction_data)
        
        # Test limit parameter
        response = self.client.get(f'/api/prediction/history?user_id={self.test_user_id}&limit=3')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['predictions']), 3)
        
        # Test offset parameter
        response = self.client.get(f'/api/prediction/history?user_id={self.test_user_id}&offset=3')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertLessEqual(len(data['predictions']), 2)  # Should have at most 2 predictions
        
        # Test combined limit and offset
        response = self.client.get(f'/api/prediction/history?user_id={self.test_user_id}&limit=2&offset=1')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['predictions']), 2)
        
    def test_image_storage(self):
        """Test saving and retrieving images with predictions"""
        # Make a prediction with image storage
        response = self.client.post(
            '/api/prediction/predict',
            data={
                'file': (self.img_bytes, 'test_image.jpg'),
                'user_id': self.test_user_id,
                'save_image': 'true'
            },
            content_type='multipart/form-data'
        )
        
        # Check response contains image path
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertIn('prediction_id', result)
        self.assertIn('image_path', result)
        prediction_id = result['prediction_id']
        
        # Get prediction with image data
        detail_response = self.client.get(f'/api/prediction/history/{prediction_id}?include_image=true')
        self.assertEqual(detail_response.status_code, 200)
        detail_data = json.loads(detail_response.data)
        
        # Verify image data is included
        self.assertIn('image_data', detail_data)
        self.assertTrue(detail_data['image_data'])  # Should be non-empty string

if __name__ == '__main__':
    unittest.main()
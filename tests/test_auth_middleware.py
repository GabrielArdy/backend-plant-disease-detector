#!/usr/bin/env python

import unittest
import os
import sys
import json
from io import BytesIO
from PIL import Image

# Add parent directory to path so we can import the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.api.auth.models import Auth
from app.api.prediction.models import PredictionHistory

class TestAuthMiddleware(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment before each test"""
        self.app = create_app('testing')
        self.client = self.app.test_client()
        
        # Create test credentials
        self.username = 'testuser'
        self.password = 'TestPassword123!'
        self.email = 'testuser@example.com'
        
        # Create a test image (black square 224x224)
        img = Image.new('RGB', (224, 224), color='black')
        self.img_bytes = BytesIO()
        img.save(self.img_bytes, format='JPEG')
        self.img_bytes.seek(0)
        
        # Register test user and get token
        with self.app.app_context():
            # Check if user already exists
            existing_user = Auth.get_user_by_username(self.username)
            if not existing_user:
                Auth.create_user(
                    first_name='Test',
                    last_name='User',
                    email=self.email,
                    username=self.username,
                    password=self.password
                )
        
        # Login to get auth token
        response = self.client.post(
            '/api/auth/login',
            json={
                'username': self.username,
                'password': self.password
            }
        )
        
        data = json.loads(response.data)
        self.auth_token = data['data']['token']
        self.user_id = data['data']['user_id']
        
    def test_predict_without_auth(self):
        """Test that prediction endpoint requires authentication"""
        # Try to predict without auth token
        response = self.client.post(
            '/api/prediction/predict',
            data={
                'file': (self.img_bytes, 'test_image.jpg')
            },
            content_type='multipart/form-data'
        )
        
        # Should get 401 Unauthorized
        self.assertEqual(response.status_code, 401)
        
        # Check error message
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertIn('Authentication required', data['message'])
    
    def test_predict_with_auth(self):
        """Test that prediction works with valid auth token"""
        # Predict with auth token
        response = self.client.post(
            '/api/prediction/predict',
            data={
                'file': (self.img_bytes, 'test_image.jpg')
            },
            headers={
                'Authorization': f'Bearer {self.auth_token}'
            },
            content_type='multipart/form-data'
        )
        
        # Should get 200 OK
        self.assertEqual(response.status_code, 200)
        
        # Should have user_id in the response
        data = json.loads(response.data)
        self.assertIn('user_id', data)
        self.assertEqual(data['user_id'], self.user_id)
    
    def test_get_prediction_history(self):
        """Test getting prediction history for authenticated user"""
        # Make a prediction first to have some history
        self.client.post(
            '/api/prediction/predict',
            data={
                'file': (self.img_bytes, 'test_image.jpg')
            },
            headers={
                'Authorization': f'Bearer {self.auth_token}'
            },
            content_type='multipart/form-data'
        )
        
        # Now get the history
        response = self.client.get(
            '/api/prediction/history',
            headers={
                'Authorization': f'Bearer {self.auth_token}'
            }
        )
        
        # Should get 200 OK
        self.assertEqual(response.status_code, 200)
        
        # Should have predictions array
        data = json.loads(response.data)
        self.assertIn('predictions', data)
        self.assertIsInstance(data['predictions'], list)
        self.assertGreater(len(data['predictions']), 0)
        
        # Should have user_id matching authenticated user
        self.assertEqual(data['user_id'], self.user_id)
    
    def test_get_prediction_detail(self):
        """Test getting detail for a specific prediction"""
        # Make a prediction first to have some history
        pred_response = self.client.post(
            '/api/prediction/predict',
            data={
                'file': (self.img_bytes, 'test_image.jpg')
            },
            headers={
                'Authorization': f'Bearer {self.auth_token}'
            },
            content_type='multipart/form-data'
        )
        
        pred_data = json.loads(pred_response.data)
        prediction_id = pred_data['prediction_id']
        
        # Now get the detail with image
        response = self.client.get(
            f'/api/prediction/history/{prediction_id}?include_image=true',
            headers={
                'Authorization': f'Bearer {self.auth_token}'
            }
        )
        
        # Should get 200 OK
        self.assertEqual(response.status_code, 200)
        
        # Should have prediction details including image data
        data = json.loads(response.data)
        self.assertEqual(data['prediction_id'], prediction_id)
        self.assertEqual(data['user_id'], self.user_id)
        
        # If image was saved, should have image data
        if 'image_path' in data:
            self.assertIn('image_data', data)
    
    def test_get_all_user_predictions(self):
        """Test getting all predictions with filters"""
        # Make a few predictions first
        for _ in range(3):
            # Create a new image for each request to avoid closed file issue
            img = Image.new('RGB', (224, 224), color='black')
            img_bytes = BytesIO()
            img.save(img_bytes, format='JPEG')
            img_bytes.seek(0)
            
            self.client.post(
                '/api/prediction/predict',
                data={
                    'file': (img_bytes, 'test_image.jpg')
                },
                headers={
                    'Authorization': f'Bearer {self.auth_token}'
                },
                content_type='multipart/form-data'
            )
        
        # Now get all predictions with filters
        response = self.client.get(
            '/api/prediction/my-predictions?limit=2&sort_order=desc',
            headers={
                'Authorization': f'Bearer {self.auth_token}'
            }
        )
        
        # Should get 200 OK
        self.assertEqual(response.status_code, 200)
        
        # Should have predictions array
        data = json.loads(response.data)
        self.assertIn('predictions', data)
        self.assertIsInstance(data['predictions'], list)
        
        # Should respect the limit
        self.assertEqual(len(data['predictions']), 2)
        
        # Should have total count greater than limit
        self.assertIn('total', data)
        self.assertGreater(data['total'], 2)

if __name__ == '__main__':
    unittest.main()

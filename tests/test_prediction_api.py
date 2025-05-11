#!/usr/bin/env python
# filepath: /home/ardy/plant-disease/backend/tests/test_prediction_api.py
import unittest
import os
import sys
import json
from io import BytesIO

# Add parent directory to path so we can import the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

class TestPredictionAPI(unittest.TestCase):
    
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
    
    def test_health_endpoint(self):
        """Test that the health endpoint returns a successful response"""
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'ok')
        self.assertEqual(data['message'], 'Plant Disease API is running')

if __name__ == '__main__':
    unittest.main()

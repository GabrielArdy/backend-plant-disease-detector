import unittest
import os
import json
from flask import Flask
import tensorflow as tf

from app import create_app
from app.utils.gpu_utils import setup_gpu, get_device_info
from app.core.models.model_loader import ModelLoader
from app.core.models.inference import InferenceModel

class TestGPUDetection(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment before each test"""
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        """Clean up after each test"""
        self.app_context.pop()

    def test_gpu_utils_functions(self):
        """Test the GPU utility functions"""
        # Test setup_gpu function
        is_using_gpu = setup_gpu()
        self.assertIsInstance(is_using_gpu, bool)
        
        # Test get_device_info function
        device_info = get_device_info()
        self.assertIsInstance(device_info, dict)
        self.assertIn('devices', device_info)
        self.assertIn('using_gpu', device_info)
        self.assertIn('num_gpus', device_info)
        
        # Check device consistency
        if device_info['using_gpu']:
            self.assertGreater(device_info['num_gpus'], 0)
        else:
            self.assertEqual(device_info['num_gpus'], 0)
        
    def test_inference_model_gpu_detection(self):
        """Test that the inference model correctly detects GPU"""
        model = InferenceModel()
        self.assertIsInstance(model.using_gpu, bool)
    
    def test_model_loader_gpu_info(self):
        """Test that the model loader correctly reports GPU information"""
        model_loader = ModelLoader()
        device_info = model_loader.get_device_information()
        
        self.assertIsInstance(device_info, dict)
        self.assertIn('devices', device_info)
        self.assertIn('using_gpu', device_info)
        self.assertIn('num_gpus', device_info)
    
    def test_system_info_endpoint(self):
        """Test the system-info API endpoint"""
        response = self.client.get('/api/prediction/system-info')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('device_info', data)
        self.assertIn('tensorflow_version', data['device_info'])
        self.assertIn('using_gpu', data['device_info'])
        self.assertIn('num_gpus', data['device_info'])
        self.assertIn('devices', data['device_info'])

    def test_health_endpoint_gpu_info(self):
        """Test that the health endpoint includes GPU information"""
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('hardware', data)
        self.assertIn('using_gpu', data['hardware'])
        self.assertIn('gpu_count', data['hardware'])
        self.assertIn('tensorflow_version', data['hardware'])

if __name__ == '__main__':
    unittest.main()

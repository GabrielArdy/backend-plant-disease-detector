import unittest
from app.services.advice_service import get_plant_disease_advice
from app.utils.log import get_logger

logger = get_logger(__name__)

class AdviceServiceTest(unittest.TestCase):
    
    def test_get_plant_disease_advice_healthy(self):
        """Test advice for healthy plants"""
        # Test with a healthy plant
        disease_info = {
            'plant_type': 'Tomato',
            'condition': 'healthy',
            'confidence': 0.95
        }
        
        advice = get_plant_disease_advice(disease_info)
        
        # Check that advice contains expected sections
        self.assertIn('treatment', advice)
        self.assertIn('prevention', advice)
        self.assertIn('additional_info', advice)
        
        # For healthy plants, treatment should be "No treatment needed"
        self.assertIn('No treatment needed', advice['treatment'])
    
    def test_get_plant_disease_advice_disease(self):
        """Test advice for diseased plants"""
        # Test with a disease
        disease_info = {
            'plant_type': 'Tomato',
            'condition': 'Early blight',
            'confidence': 0.85
        }
        
        advice = get_plant_disease_advice(disease_info)
        
        # Check that advice contains expected sections
        self.assertIn('treatment', advice)
        self.assertIn('prevention', advice)
        self.assertIn('additional_info', advice)
        
        # Log the advice for manual inspection
        logger.info(f"Generated advice: {advice}")
        
        # Make sure the advice is not empty
        self.assertTrue(len(advice['treatment']) > 0)
        self.assertTrue(len(advice['prevention']) > 0)
        self.assertTrue(len(advice['additional_info']) > 0)
    
    def test_fallback_advice(self):
        """Test that fallback advice is provided when API key is missing temporarily"""
        import os
        
        # Store original API key
        original_key = os.environ.get('GENAI_API_KEY')
        
        try:
            # Temporarily unset the API key
            if 'GENAI_API_KEY' in os.environ:
                del os.environ['GENAI_API_KEY']
            
            # Test with a disease
            disease_info = {
                'plant_type': 'Tomato',
                'condition': 'Early blight',
                'confidence': 0.85
            }
            
            advice = get_plant_disease_advice(disease_info)
            
            # Check that advice contains expected sections
            self.assertIn('treatment', advice)
            self.assertIn('prevention', advice)
            self.assertIn('additional_info', advice)
            
            # Check if error indicates we're using fallback advice
            self.assertIsNotNone(advice['error'])
            self.assertIn('fallback', advice['error'].lower())
            
        finally:
            # Restore original API key
            if original_key is not None:
                os.environ['GENAI_API_KEY'] = original_key

if __name__ == '__main__':
    unittest.main()

"""
Simplified test for the AI advice feature
"""

import unittest
from app.services.advice_service import _get_fallback_advice

class TestGeminiAdvice(unittest.TestCase):
    
    def test_fallback_advice(self):
        """Test the fallback advice functionality"""
        # Test tomato early blight
        disease_info = {
            'plant_type': 'tomato',
            'condition': 'Early Blight',
            'confidence': 0.92
        }
        
        advice = _get_fallback_advice(disease_info)
        
        # Check structure
        self.assertIsNotNone(advice)
        self.assertIn('treatment', advice)
        self.assertIn('prevention', advice)
        self.assertIn('additional_info', advice)
        self.assertIn('error', advice)
        
        # Check content - should reference blight
        self.assertIn('blight', advice['additional_info'].lower())
        
        # Check treatment includes key terms
        blight_terms = ['fungicide', 'remove', 'infected']
        self.assertTrue(any(term.lower() in advice['treatment'].lower() for term in blight_terms))
    
    def test_general_fallback(self):
        """Test fallback for unsupported plants"""
        disease_info = {
            'plant_type': 'banana',  # Not in fallback dictionary
            'condition': 'Panama Disease',
            'confidence': 0.85
        }
        
        advice = _get_fallback_advice(disease_info)
        
        # Check structure 
        self.assertIsNotNone(advice)
        self.assertIn('treatment', advice)
        self.assertIn('prevention', advice)
        self.assertIn('additional_info', advice)
        self.assertIn('error', advice)
        
        # Should have generic advice
        self.assertIn('generic', advice['error'].lower())
        self.assertIn('crop rotation', advice['prevention'].lower())

if __name__ == '__main__':
    unittest.main()

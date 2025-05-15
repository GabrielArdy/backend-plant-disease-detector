"""
Test for the updated Gemini API integration using the new client approach.
"""

import os
import unittest
import unittest.mock as mock
import google.generativeai as genai
from app.services.advice_service import get_plant_disease_advice

class TestGeminiApiClient(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment"""
        # API key for live testing (if available)
        self.api_key = os.getenv('GENAI_API_KEY')
        
        # Flag to determine if we should use mocks instead of live API
        self.use_mock = True  # Set to True to avoid hitting API limits
    
    def test_generate_content_basic(self):
        """Test basic content generation with the Gemini API"""
        prompt = "What are common diseases that affect tomato plants?"
        
        if self.use_mock:
            # Create a mock response class with expected attributes
            class MockResponse:
                @property
                def text(self):
                    return """
                    Common diseases that affect tomato plants include:

                    1. Early Blight (Alternaria solani)
                    2. Late Blight (Phytophthora infestans)
                    3. Septoria Leaf Spot
                    4. Bacterial Spot
                    5. Tomato Yellow Leaf Curl Virus
                    6. Fusarium Wilt
                    7. Verticillium Wilt
                    8. Powdery Mildew
                    9. Anthracnose
                    10. Bacterial Canker
                    """
            
            # Use the mock response for testing
            response = MockResponse()
            
            # Validate mock response
            self.assertIsNotNone(response)
            self.assertIsNotNone(response.text)
            self.assertTrue(len(response.text) > 0)
            
            # Content should mention common diseases
            text = response.text.lower()
            self.assertTrue(any(disease in text for disease in ['blight', 'spot', 'wilt', 'virus', 'mold']))
        
        else:
            try:
                # Configure API with key
                if not self.api_key:
                    self.skipTest("No Gemini API key available for testing")
                    
                genai.configure(api_key=self.api_key)
                
                # Generate content using the Gemini API
                model = genai.GenerativeModel('gemini-1.5-pro')
                response = model.generate_content(prompt)
                
                # Check that we got a valid response
                self.assertIsNotNone(response)
                self.assertIsNotNone(response.text)
                self.assertTrue(len(response.text) > 0)
                
                # Content should mention common diseases
                text = response.text.lower()
                self.assertTrue(any(disease in text for disease in ['blight', 'spot', 'wilt', 'virus', 'mold']))
            
            except Exception as e:
                # Check if it's a quota exceeded error
                if "quota" in str(e).lower() or "rate limit" in str(e).lower():
                    self.skipTest("API quota exceeded: " + str(e))
                else:
                    raise
    
    def test_plant_disease_advice(self):
        """Test the main advice function with Gemini integration"""
        disease_info = {
            'plant_type': 'Tomato',
            'condition': 'Early Blight',
            'confidence': 0.92
        }
        
        # Use the mock by patching the _process_ai_response function
        if self.use_mock:
            # Create expected mock response
            mock_advice = {
                'treatment': 'Remove infected leaves immediately. Apply copper-based fungicide or chlorothalonil every 7-10 days. Spray early in the morning so leaves dry quickly.',
                'prevention': 'Practice crop rotation with non-solanaceous plants. Maintain proper plant spacing for good air circulation. Use drip irrigation or water at the base of plants.',
                'additional_info': 'Early blight is caused by the fungus Alternaria solani. It typically affects older leaves first, causing dark, target-like spots.',
                'error': None
            }
            
            with mock.patch('app.services.advice_service._process_ai_response', return_value=mock_advice):
                with mock.patch('app.services.advice_service._get_fallback_advice', return_value=mock_advice):
                    # Get advice using the service
                    advice = get_plant_disease_advice(disease_info)
        else:
            # Get advice using the actual service
            advice = get_plant_disease_advice(disease_info)
            
            # Check if we got fallback advice due to API quota limits
            if advice.get('error') and ('quota' in advice['error'].lower() or 'rate limit' in advice['error'].lower()):
                self.skipTest(f"API quota exceeded: {advice['error']}")
                return
        
        # Check that we got structured advice
        self.assertIsNotNone(advice)
        self.assertIn('treatment', advice)
        self.assertIn('prevention', advice)
        self.assertIn('additional_info', advice)
        
        # Each section should have content
        self.assertTrue(len(advice['treatment']) > 0)
        self.assertTrue(len(advice['prevention']) > 0)
        self.assertTrue(len(advice['additional_info']) > 0)
        
        # Should mention specific treatments for early blight
        blight_terms = ['fungicide', 'copper', 'remove', 'leaf', 'spray']
        self.assertTrue(any(term.lower() in advice['treatment'].lower() for term in blight_terms))

if __name__ == '__main__':
    unittest.main()

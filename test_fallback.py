"""
Simple test for the advice service fallback functionality
"""

from app.services.advice_service import _get_fallback_advice

def test_fallback():
    # Test tomato early blight
    disease_info = {
        'plant_type': 'tomato',
        'condition': 'Early Blight',
        'confidence': 0.92
    }
    
    advice = _get_fallback_advice(disease_info)
    print("\nTomato Early Blight Advice:")
    print(f"Treatment: {advice['treatment']}")
    print(f"Prevention: {advice['prevention']}")
    print(f"Additional Info: {advice['additional_info']}")
    print(f"Error: {advice['error']}")
    
    # Test corn rust
    disease_info = {
        'plant_type': 'corn',
        'condition': 'Common Rust',
        'confidence': 0.88
    }
    
    advice = _get_fallback_advice(disease_info)
    print("\nCorn Common Rust Advice:")
    print(f"Treatment: {advice['treatment']}")
    print(f"Prevention: {advice['prevention']}")
    print(f"Additional Info: {advice['additional_info']}")
    print(f"Error: {advice['error']}")
    
    # Test unknown plant
    disease_info = {
        'plant_type': 'banana',
        'condition': 'Panama Disease',
        'confidence': 0.85
    }
    
    advice = _get_fallback_advice(disease_info)
    print("\nBanana Panama Disease Advice (unknown plant):")
    print(f"Treatment: {advice['treatment']}")
    print(f"Prevention: {advice['prevention']}")
    print(f"Additional Info: {advice['additional_info']}")
    print(f"Error: {advice['error']}")

if __name__ == "__main__":
    print("Testing fallback advice functionality...")
    test_fallback()
    print("\nTest completed!")

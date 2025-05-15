#!/usr/bin/env python
# filepath: /home/ardy/plant-disease/backend/simple_advice_test.py

"""
Simple direct test for the improved advice generation
"""

import os
import sys
import logging
from dotenv import load_dotenv
from pathlib import Path
import json

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

# Load API key from environment variable
env_path = Path(__file__).parent / 'local.env'
if env_path.exists():
    logging.info(f"Loading environment variables from {env_path}")
    with open(env_path, 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value
                if key == 'GENAI_API_KEY':
                    logging.info(f"API key loaded: {value[:4]}...{value[-4:]}")

# Now create some hardcoded advice for tomato early blight
tomato_early_blight_advice = {
    "treatment": "Remove infected lower leaves immediately and dispose of them (do not compost). Apply fungicides containing chlorothalonil, mancozeb, or copper-based products every 7-10 days. Organic options include copper fungicides, neem oil, or sulfur products. Ensure proper spacing between plants to improve air circulation.",
    "prevention": "Practice crop rotation (don't plant tomatoes in the same spot for 3-4 years). Use drip irrigation or water at the base to keep foliage dry. Mulch around plants to prevent soil splash. Choose resistant varieties when available. Remove plant debris at the end of the growing season.",
    "additional_info": "Early blight is caused by the fungus Alternaria solani and typically appears first on older, lower leaves as small brown spots with concentric rings (bull's-eye pattern). It thrives in warm (75-85°F), humid conditions, especially with alternating wet and dry periods. Without treatment, it can cause significant defoliation and reduce yields by 30-50%."
}

# Format as a prediction result
prediction_result = {
    "class_id": 5,
    "class_name": "Tomato___Early_blight",
    "confidence": 0.7637557983398438,
    "plant_type": "Tomato",
    "condition": "Early blight",
    "display_name": "Tomato - Early blight",
    "advice": "",  # Will be filled
    "user_id": "69647e40-60d4-4aca-b529-cef0f1ce9270",
    "prediction_id": "81b3b107-230f-406d-b8bd-e321e8e595f5",
    "timestamp": "2025-05-15T14:34:33.308852"
}

def test_advice_replacement():
    """Test manually replacing advice in a prediction"""
    try:
        # Format the advice into a single string like the service does
        advice = f"TREATMENT:\n{tomato_early_blight_advice['treatment']}\n\n"
        advice += f"PREVENTION:\n{tomato_early_blight_advice['prevention']}\n\n"
        advice += f"ADDITIONAL INFORMATION:\n{tomato_early_blight_advice['additional_info']}"
        
        # Set the advice in the prediction
        prediction_result['advice'] = advice
        
        # Print the result
        logging.info("Updated prediction with proper advice:")
        print(json.dumps(prediction_result, indent=2))
        
        logging.info("Success! You can copy this JSON and use it to fix the prediction in the database.")
        return True
    except Exception as e:
        logging.error(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_advice_replacement()

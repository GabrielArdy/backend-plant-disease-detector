#!/usr/bin/env python
# filepath: /home/ardy/plant-disease/backend/test_advice.py

"""
Test script to diagnose issues with the Gemini AI advice generation
"""

import os
import sys
import logging
from dotenv import load_dotenv
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout)])

# Load environment variables
env_path = Path(__file__).parent / 'local.env'
if env_path.exists():
    print(f"Loading environment variables from {env_path}")
    load_dotenv(dotenv_path=env_path)
    
    # Ensure the API key is loaded
    with open(env_path, 'r') as f:
        for line in f:
            if line.startswith('GENAI_API_KEY='):
                api_key = line.strip().split('=', 1)[1]
                os.environ['GENAI_API_KEY'] = api_key
                print(f"API key loaded: {api_key[:5]}...{api_key[-4:]}")
                break
else:
    print(f"Environment file {env_path} not found")

# Import the advice service functions
from app.services.advice_service import (
    check_gemini_connection,
    get_plant_disease_advice,
    get_gemini_advice_for_disease
)

# Test connection
print("\n--- Testing Gemini API Connection ---")
connection_status = check_gemini_connection()
print(f"Connection available: {connection_status['available']}")
print(f"Model name: {connection_status['model_name']}")
if connection_status.get('error'):
    print(f"Error: {connection_status['error']}")

if connection_status.get('model_details'):
    print(f"Model details: {connection_status['model_details']}")

# Test advice for Tomato Early Blight
print("\n--- Testing Advice for Tomato Early Blight ---")

# Test 1: Using get_plant_disease_advice
print("\nTest 1: get_plant_disease_advice")
disease_info = {
    'plant_type': 'Tomato',
    'condition': 'Early blight',
    'confidence': 0.95
}

try:
    advice = get_plant_disease_advice(disease_info)
    print("\nTreatment:")
    print(advice['treatment'])
    print("\nPrevention:")
    print(advice['prevention'])
    print("\nAdditional Info:")
    print(advice['additional_info'])
    if advice.get('error'):
        print(f"\nError: {advice['error']}")
except Exception as e:
    print(f"Error generating advice: {e}")

# Test 2: Using get_gemini_advice_for_disease
print("\nTest 2: get_gemini_advice_for_disease")
try:
    disease_name = "Tomato___Early_blight"
    advice_text = get_gemini_advice_for_disease(disease_name)
    print("\nAdvice:")
    print(advice_text)
except Exception as e:
    print(f"Error generating advice: {e}")

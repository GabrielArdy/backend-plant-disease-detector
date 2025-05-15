#!/usr/bin/env python
# filepath: /home/ardy/plant-disease/backend/test_full_integration.py

"""
Integration test script for the plant disease detection app
Tests both GridFS storage and advice generation functionality
"""

import os
import sys
import requests
import json
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

# API base URL (assuming Flask is running locally)
API_BASE = "http://localhost:5000/api"

# Test image path (you need to put a tomato early blight image in this location)
TEST_IMAGE_PATH = Path(__file__).parent / "test_data" / "tomato_early_blight.jpg"

# Ensure test directory exists
test_dir = Path(__file__).parent / "test_data"
test_dir.mkdir(exist_ok=True)

# If no test image exists, create a placeholder text file to notify the user
if not TEST_IMAGE_PATH.exists():
    placeholder_path = test_dir / "PLACE_TOMATO_EARLY_BLIGHT_IMAGE_HERE.txt"
    with open(placeholder_path, "w") as f:
        f.write("Please place a tomato early blight image in this directory and name it 'tomato_early_blight.jpg'")
    logger.warning(f"Test image not found at {TEST_IMAGE_PATH}")
    logger.info(f"Created placeholder at {placeholder_path}")
    logger.info("Please add a test image before running this script again")
    sys.exit(1)

# Test user credentials
test_user = {
    "username": "demo@example.com",
    "password": "demo123"
}

def login():
    """Log in and get authentication token"""
    try:
        response = requests.post(
            f"{API_BASE}/auth/login",
            json=test_user
        )
        response.raise_for_status()
        token = response.json().get("access_token")
        if not token:
            logger.error("No access token returned")
            sys.exit(1)
        
        logger.info("Successfully logged in")
        return token
    except requests.RequestException as e:
        logger.error(f"Login failed: {e}")
        sys.exit(1)

def upload_image(token):
    """Test image upload to GridFS"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        with open(TEST_IMAGE_PATH, "rb") as image_file:
            files = {"file": (TEST_IMAGE_PATH.name, image_file, "image/jpeg")}
            
            response = requests.post(
                f"{API_BASE}/images/upload",
                headers=headers,
                files=files
            )
            
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"Successfully uploaded image: {result.get('file_id')}")
            return result.get('file_id')
    except requests.RequestException as e:
        logger.error(f"Upload failed: {e}")
        if hasattr(e, "response"):
            logger.error(f"Response: {e.response.text}")
        sys.exit(1)

def predict_disease(token, file_id):
    """Test disease prediction with the uploaded image"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        data = {"file_id": file_id}
        
        response = requests.post(
            f"{API_BASE}/predict",
            headers=headers,
            json=data
        )
        
        response.raise_for_status()
        result = response.json()
        
        logger.info(f"Prediction received: {result.get('class_name')}")
        
        # Check if this is a tomato early blight prediction
        if result.get('class_name') == "Tomato___Early_blight":
            logger.info("Detected Tomato Early Blight, checking for proper advice...")
            
            # Check if advice is present and has expected content
            advice = result.get('advice', '')
            if "TREATMENT:" in advice and "PREVENTION:" in advice and len(advice) > 200:
                logger.info("SUCCESS: Proper advice was generated for Tomato Early Blight")
            else:
                logger.error(f"FAILED: Advice content doesn't look right: {advice[:100]}...")
        
        return result
    except requests.RequestException as e:
        logger.error(f"Prediction failed: {e}")
        if hasattr(e, "response"):
            logger.error(f"Response: {e.response.text}")
        sys.exit(1)

def run_test():
    """Run the full integration test"""
    logger.info("Starting integration test")
    
    # Step 1: Login
    token = login()
    
    # Step 2: Upload image (tests GridFS)
    file_id = upload_image(token)
    
    # Step 3: Make prediction (tests advice generation)
    prediction = predict_disease(token, file_id)
    
    # Print full prediction
    logger.info("Test completed. Full prediction result:")
    print(json.dumps(prediction, indent=2))

if __name__ == "__main__":
    run_test()

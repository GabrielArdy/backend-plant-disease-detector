#!/usr/bin/env python
# filepath: /home/ardy/plant-disease/backend/health_test.py

"""
Quick script to directly test our health endpoint
"""

import sys
import logging
import requests

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def test_health_endpoint(base_url="http://localhost:5000"):
    """Test the health endpoint"""
    try:
        url = f"{base_url}/api/health"
        response = requests.get(url)
        
        if response.status_code == 200:
            logger.info(f"Health endpoint is working! Status code: {response.status_code}")
            logger.info(response.json())
            return True
        else:
            logger.error(f"Health endpoint failed with status code: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
    except requests.RequestException as e:
        logger.error(f"Failed to connect to health endpoint: {e}")
        return False

if __name__ == "__main__":
    logger.info("Testing health endpoint...")
    if test_health_endpoint():
        sys.exit(0)
    else:
        logger.error("Health endpoint test failed")
        sys.exit(1)

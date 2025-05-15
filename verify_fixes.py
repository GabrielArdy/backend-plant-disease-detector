#!/usr/bin/env python
# filepath: /home/ardy/plant-disease/backend/verify_fixes.py

"""
Simple verification script that tests our fixes
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

def check_server_status():
    """Check if the server is running"""
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            logger.info("Server is running")
            return True
        else:
            logger.warning(f"Server returned status code {response.status_code}")
            return False
    except requests.RequestException as e:
        logger.error(f"Failed to connect to server: {e}")
        logger.info("Make sure the server is running: cd /home/ardy/plant-disease/backend && flask run")
        return False

def login():
    """Log in and get authentication token"""
    try:
        response = requests.post(
            f"{API_BASE}/auth/login",
            json={"username": "demo@example.com", "password": "demo123"}
        )
        
        if response.status_code != 200:
            logger.error(f"Login failed with status {response.status_code}: {response.text}")
            return None
            
        token = response.json().get("access_token")
        if not token:
            logger.error("No access token returned")
            return None
        
        logger.info("Successfully logged in")
        return token
    except requests.RequestException as e:
        logger.error(f"Login failed: {e}")
        return None

def check_database_connection():
    """Check if MongoDB is properly connected"""
    try:
        from app.extensions import mongo
        from flask import current_app
        
        from app import create_app
        app = create_app()
        
        with app.app_context():
            collections = mongo.db.list_collection_names()
            logger.info(f"Connected to MongoDB. Collections: {collections}")
            return True
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        return False

def check_gridfs():
    """Check if GridFS is properly initialized"""
    try:
        from app.extensions import fs
        from flask import current_app
        from gridfs import GridFS
        
        from app import create_app
        app = create_app()
        
        with app.app_context():
            files = list(fs.find().limit(5))
            logger.info(f"GridFS is working. Found {len(files)} files")
            if files:
                logger.info(f"Latest file ID: {files[-1]._id}")
            return True
    except Exception as e:
        logger.error(f"GridFS check failed: {e}")
        return False

def check_advice_service():
    """Check if advice service is properly working"""
    try:
        from app.services.advice_service import get_advice_for_condition
        from flask import current_app
        
        from app import create_app
        app = create_app()
        
        with app.app_context():
            # Get advice for tomato early blight
            advice_dict = get_advice_for_condition("Tomato", "Early blight")
            advice = ""
            
            # Format the advice into a string
            if isinstance(advice_dict, dict):
                if 'treatment' in advice_dict:
                    advice += f"TREATMENT:\n{advice_dict.get('treatment', '')}\n\n"
                if 'prevention' in advice_dict:
                    advice += f"PREVENTION:\n{advice_dict.get('prevention', '')}\n\n"
                if 'additional_info' in advice_dict:
                    advice += f"ADDITIONAL INFORMATION:\n{advice_dict.get('additional_info', '')}"
            elif isinstance(advice_dict, str):
                advice = advice_dict
            
            if advice and len(advice) > 100:
                logger.info(f"Advice service is working. Got advice of length {len(advice)}")
                logger.info(f"Sample: {advice[:100]}...")
                return True
            else:
                logger.error(f"Advice too short or empty: {advice}")
                return False
    except Exception as e:
        logger.error(f"Advice service check failed: {e}")
        return False

def main():
    """Run all verification checks"""
    logger.info("Starting fix verification")
    
    # Check if server is running
    if not check_server_status():
        logger.warning("Skipping server-based tests")
    else:
        # Try to log in to verify API
        token = login()
        if token:
            logger.info("API authentication is working")
    
    # Check direct database connection
    check_database_connection()
    
    # Check GridFS connection
    check_gridfs()
    
    # Check advice service
    check_advice_service()
    
    logger.info("Verification complete")

if __name__ == "__main__":
    main()

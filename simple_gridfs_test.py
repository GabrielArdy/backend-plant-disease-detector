#!/usr/bin/env python
# filepath: /home/ardy/plant-disease/backend/simple_gridfs_test.py
"""
Simple direct test of GridFS functionality
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient
from gridfs import GridFS
import io
from PIL import Image

# Load environment variables
env_path = Path(__file__).parent / 'local.env'
if env_path.exists():
    print(f"Loading environment variables from {env_path}")
    load_dotenv(dotenv_path=env_path)
else:
    print(f"Environment file {env_path} not found")

def simple_gridfs_test():
    """Simple direct test of GridFS"""
    try:
        # Get MongoDB URI
        mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/plant_disease_dev')
        print(f"Using MongoDB URI: {mongo_uri}")
        
        # Connect directly to MongoDB
        print("Connecting to MongoDB...")
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        
        # Get database name from URI
        db_name = mongo_uri.split('/')[-1]
        db = client[db_name]
        print(f"Connected to database: {db_name}")
        
        # Initialize GridFS directly
        print("Initializing GridFS...")
        fs = GridFS(db)
        
        # Create a test image
        print("Creating test image...")
        img = Image.new('RGB', (100, 100), color='green')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        # Save to GridFS
        print("Saving image to GridFS...")
        file_id = fs.put(img_bytes.read(), filename='simple_test.jpg', content_type='image/jpeg')
        print(f"Image saved with ID: {file_id}")
        
        # Retrieve from GridFS
        print("Retrieving image from GridFS...")
        retrieved = fs.get(file_id)
        print(f"Retrieved image: {retrieved.filename}, {retrieved.content_type}")
        
        # Clean up
        print("Deleting test image...")
        fs.delete(file_id)
        
        print("Test completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    simple_gridfs_test()

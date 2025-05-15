#!/usr/bin/env python
# filepath: /home/ardy/plant-disease/backend/diagnose_mongo.py
"""
Diagnostic script for MongoDB and GridFS
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient
from gridfs import GridFS
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import io
from PIL import Image

# Load environment variables
env_path = Path(__file__).parent / 'local.env'
load_dotenv(dotenv_path=env_path)

def test_mongo_connection():
    """Test direct MongoDB connection"""
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/plant_disease_dev')
    print(f"Testing MongoDB connection to: {mongo_uri}")
    
    try:
        # Set a short timeout for faster feedback
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        
        # The ismaster command is cheap and does not require auth
        client.admin.command('ismaster')
        print("MongoDB connection successful!")
        
        # Test database access
        db_name = mongo_uri.split('/')[-1]
        db = client[db_name]
        print(f"Accessed database: {db_name}")
        
        # List collections
        collections = db.list_collection_names()
        print(f"Collections: {collections}")
        
        # Test GridFS directly
        fs = GridFS(db)
        print("GridFS initialized successfully")
        
        # Test GridFS operations
        test_gridfs_operations(fs)
        
        return True
        
    except ConnectionFailure as e:
        print(f"MongoDB connection failed: {e}")
        return False
    except ServerSelectionTimeoutError as e:
        print(f"MongoDB server selection timeout: {e}")
        print("Check if MongoDB is running and accessible")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def test_gridfs_operations(fs):
    """Test GridFS operations directly"""
    try:
        # Create a simple test image
        print("Creating test image...")
        img = Image.new('RGB', (100, 100), color='blue')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        # Metadata for the image
        metadata = {
            'content_type': 'image/jpeg',
            'filename': 'diagnostic_test.jpg',
            'test': True
        }
        
        # Try saving to GridFS
        print("Saving image to GridFS...")
        file_id = fs.put(img_bytes.read(), **metadata)
        print(f"Image saved with ID: {file_id}")
        
        # Try retrieving from GridFS
        print("Retrieving image from GridFS...")
        retrieved = fs.get(file_id)
        
        # Verify metadata
        print(f"Content type: {retrieved.content_type}")
        print(f"Filename: {retrieved.filename}")
        
        # Delete the test file
        print("Deleting test image...")
        fs.delete(file_id)
        
        print("GridFS operations test completed successfully!")
    except Exception as e:
        print(f"GridFS operations test failed: {e}")

if __name__ == "__main__":
    test_mongo_connection()

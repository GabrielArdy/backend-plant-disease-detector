#!/usr/bin/env python
# filepath: /home/ardy/plant-disease/backend/fix_tomato_advice.py

"""
This script directly fixes the tomato early blight advice in the database
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
from bson.objectid import ObjectId

# Load environment variables
env_path = Path(__file__).parent / 'local.env'
load_dotenv(dotenv_path=env_path)

# Get MongoDB URI from environment variables
mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/plant_disease_dev')
print(f"Connecting to MongoDB at: {mongo_uri}")

# Connect to MongoDB
client = MongoClient(mongo_uri)
db_name = mongo_uri.split('/')[-1]
db = client[db_name]
print(f"Connected to database: {db_name}")

# Define the corrected advice for tomato early blight
tomato_early_blight_advice = """TREATMENT:
Remove infected lower leaves immediately and dispose of them (do not compost). Apply fungicides containing chlorothalonil, mancozeb, or copper-based products every 7-10 days. Organic options include copper fungicides, neem oil, or sulfur products. Ensure proper spacing between plants to improve air circulation.

PREVENTION:
Practice crop rotation (don't plant tomatoes in the same spot for 3-4 years). Use drip irrigation or water at the base to keep foliage dry. Mulch around plants to prevent soil splash. Choose resistant varieties when available. Remove plant debris at the end of the growing season.

ADDITIONAL INFORMATION:
Early blight is caused by the fungus Alternaria solani and typically appears first on older, lower leaves as small brown spots with concentric rings (bull's-eye pattern). It thrives in warm (75-85°F), humid conditions, especially with alternating wet and dry periods. Without treatment, it can cause significant defoliation and reduce yields by 30-50%."""

# Fix specific prediction with empty advice
def fix_prediction(prediction_id=None, class_name="Tomato___Early_blight"):
    """Fix a specific prediction or all predictions for a class"""
    collection = db.prediction_history
    
    # Create query
    query = {"class_name": class_name}
    if prediction_id:
        query["prediction_id"] = prediction_id
    
    # Find predictions to update
    predictions = list(collection.find(query))
    print(f"Found {len(predictions)} predictions to update")
    
    # Update advice for each prediction
    updated_count = 0
    for pred in predictions:
        old_advice = pred.get('advice', '')
        if "No specific treatment information was generated" in old_advice:
            # Update the prediction with proper advice
            result = collection.update_one(
                {"_id": pred["_id"]},
                {"$set": {"advice": tomato_early_blight_advice}}
            )
            
            if result.modified_count > 0:
                updated_count += 1
                print(f"Updated prediction: {pred['prediction_id']}")
            
    print(f"Updated {updated_count} predictions with proper advice")
    return updated_count

# Fix the specific prediction from the example
specific_id = "81b3b107-230f-406d-b8bd-e321e8e595f5"
print(f"Attempting to fix specific prediction: {specific_id}")
fixed = fix_prediction(prediction_id=specific_id)

# If the specific prediction wasn't found, try to fix all tomato early blight predictions
if fixed == 0:
    print("Specific prediction not found. Updating all tomato early blight predictions...")
    fix_prediction()

print("Done!")

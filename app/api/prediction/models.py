from datetime import datetime
from app.extensions import mongo
from app.utils.log import get_logger
import os
from bson import json_util
import json

logger = get_logger(__name__)

class PredictionHistory:
    """
    Model for storing prediction history in MongoDB
    """
    
    @staticmethod
    def save_prediction(prediction_data):
        """
        Save a prediction to the database
        
        Args:
            prediction_data (dict): Prediction data including:
                - prediction_id: Unique ID for this prediction
                - user_id: ID of the user who made the prediction (optional)
                - class_name: Predicted class name
                - confidence: Confidence score
                - timestamp: When the prediction was made
                - plant_type: Type of plant
                - condition: Plant condition (disease or healthy)
                - image_path: Path to the saved image (optional)
        
        Returns:
            str: The prediction_id of the saved prediction
        """
        try:
            # Ensure required fields are present
            required_fields = ['prediction_id', 'class_name', 'confidence', 'timestamp']
            for field in required_fields:
                if field not in prediction_data:
                    logger.error(f"Missing required field '{field}' in prediction data")
                    return None
            
            # Set default user_id if not provided
            if 'user_id' not in prediction_data or not prediction_data['user_id']:
                prediction_data['user_id'] = 'anonymous'
                
            # Add created_at timestamp
            prediction_data['created_at'] = datetime.utcnow()
            
            # Check if image_path is a GridFS ID (not a file path)
            if 'image_path' in prediction_data and prediction_data['image_path']:
                if '/' not in prediction_data['image_path']:
                    prediction_data['storage_type'] = 'gridfs'
                else:
                    prediction_data['storage_type'] = 'filesystem'
                    
            # Insert into MongoDB
            mongo.db.prediction_history.insert_one(prediction_data)
            logger.info(f"Prediction saved with ID {prediction_data['prediction_id']}")
            
            return prediction_data['prediction_id']
            
        except Exception as e:
            logger.error(f"Error saving prediction: {str(e)}")
            return None
    
    @staticmethod
    def get_user_predictions(user_id, limit=20, offset=0):
        """
        Get prediction history for a specific user
        
        Args:
            user_id (str): User ID
            limit (int): Maximum number of results to return
            offset (int): Number of results to skip (for pagination)
            
        Returns:
            list: List of prediction records
        """
        try:
            if not user_id:
                logger.error("No user_id provided for prediction history query")
                return []
                
            cursor = mongo.db.prediction_history.find(
                {'user_id': user_id}
            ).sort('timestamp', -1).skip(offset).limit(limit)
            
            # Convert MongoDB cursor to list and handle ObjectId serialization
            predictions = json.loads(json_util.dumps(list(cursor)))
            
            logger.info(f"Retrieved {len(predictions)} predictions for user {user_id}")
            return predictions
            
        except Exception as e:
            logger.error(f"Error retrieving user predictions: {str(e)}")
            return []
    
    @staticmethod
    def get_prediction_by_id(prediction_id):
        """
        Get a specific prediction by ID
        
        Args:
            prediction_id (str): ID of the prediction to retrieve
            
        Returns:
            dict: Prediction record or None if not found
        """
        try:
            prediction = mongo.db.prediction_history.find_one({'prediction_id': prediction_id})
            
            if prediction:
                # Convert MongoDB document to JSON-serializable dict
                prediction = json.loads(json_util.dumps(prediction))
                logger.info(f"Retrieved prediction {prediction_id}")
                return prediction
            else:
                logger.warning(f"Prediction {prediction_id} not found")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving prediction by ID: {str(e)}")
            return None
            
    @staticmethod
    def get_filtered_predictions(filters, sort_by='timestamp', sort_order='desc', limit=100, offset=0):
        """
        Get prediction history with filters
        
        Args:
            filters (dict): Dictionary of filters to apply (e.g., {'user_id': '123', 'plant_type': 'Tomato'})
            sort_by (str): Field to sort by
            sort_order (str): Sort order ('asc' or 'desc')
            limit (int): Maximum number of results to return
            offset (int): Number of results to skip (for pagination)
            
        Returns:
            list: List of filtered prediction records
        """
        try:
            # Determine sort direction
            sort_direction = -1 if sort_order == 'desc' else 1
            
            # Execute query
            cursor = mongo.db.prediction_history.find(
                filters
            ).sort(sort_by, sort_direction).skip(offset).limit(limit)
            
            # Convert MongoDB cursor to list and handle ObjectId serialization
            predictions = json.loads(json_util.dumps(list(cursor)))
            
            logger.info(f"Retrieved {len(predictions)} filtered predictions")
            return predictions
            
        except Exception as e:
            logger.error(f"Error retrieving filtered predictions: {str(e)}")
            return []
            
    @staticmethod
    def count_user_predictions(user_id):
        """
        Count total number of predictions for a user
        
        Args:
            user_id (str): User ID
            
        Returns:
            int: Total count of predictions
        """
        try:
            return mongo.db.prediction_history.count_documents({'user_id': user_id})
        except Exception as e:
            logger.error(f"Error counting user predictions: {str(e)}")
            return 0

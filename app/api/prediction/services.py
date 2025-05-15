import tensorflow as tf
import numpy as np
from PIL import Image
import io
import os
from app.core.models.model_loader import ModelLoader
from app.utils.log import get_logger
from app.utils.image import prep_image
from app.api.prediction.models import PredictionHistory

# Initialize logger
logger = get_logger(__name__)

class PredictionService:
    # Initialize model loader as a singleton
    _model_loader = None
    
    @classmethod
    def _get_model_loader(cls):
        """Get or initialize the model loader singleton"""
        if cls._model_loader is None:
            cls._model_loader = ModelLoader()
            cls._model_loader.load_model()
        return cls._model_loader
    
    # Using the prep_image utility function instead of a static method
    
    @classmethod
    def predict_disease(cls, image_file, user_id=None):
        """
        Predict plant disease from image
        
        Args:
            image_file: The uploaded image file
            user_id: Optional user ID to associate with this prediction
            
        Returns:
            dict: Prediction result including disease information
        """
        try:
            # Preprocess image using util function
            preprocessed_image = prep_image(image_file)
            
            # Get model loader
            model_loader = cls._get_model_loader()
            
            # Make prediction
            prediction = model_loader.predict(preprocessed_image)
            
            # Add additional information about the disease
            cls._add_disease_information(prediction)
            
            # Ensure user_id is set to something if provided
            if user_id:
                prediction['user_id'] = user_id
            
            return prediction
        except Exception as e:
            logger.error(f"Disease prediction error: {str(e)}")
            return {
                "error": str(e),
                "class_name": "Unknown",
                "confidence": 0.0
            }
    
    @classmethod
    def _add_disease_information(cls, prediction):
        """
        Add additional information to prediction result
        """
        if 'class_name' in prediction:
            disease_name = prediction['class_name']
            
            # Parse plant type and condition from class name
            parts = disease_name.split("___")
            plant_type = parts[0].replace("_", " ")
            condition = parts[1].replace("_", " ") if len(parts) > 1 else "Unknown"
            
            # Add plant type and condition to prediction
            prediction['plant_type'] = plant_type
            prediction['condition'] = condition
            
            # Add display name
            prediction['display_name'] = f"{plant_type} - {condition}"
            
            # Add advice for treating the disease
            prediction['advice'] = cls._get_advice_for_disease(disease_name)
    
    @staticmethod
    def _get_advice_for_disease(disease_name):
        """
        Return advice for the detected plant disease
        
        Now using Gemini AI for enhanced advice generation through the advice_service
        """
        try:
            # First try to use Gemini AI-powered advice
            from app.services.advice_service import get_gemini_advice_for_disease
            
            return get_gemini_advice_for_disease(disease_name)
        except Exception as e:
            logger.error(f"Error getting AI advice: {str(e)}. Falling back to basic advice.")
            
            # Fallback to basic advice if AI advice fails
            default_advice = "Please consult with a plant pathologist for accurate diagnosis and treatment."
            
            # Parse the disease name from format: "PlantType___Condition"
            parts = disease_name.split("___")
            plant_type = parts[0].lower()
            condition = parts[1].lower() if len(parts) > 1 else ""
            
            # Check if this is a healthy plant
            if "healthy" in condition:
                return "Your plant appears healthy! Continue with regular care and monitoring."
        
        # Very basic advice mapping - this should be expanded
        advice_map = {
            # Corn diseases
            "corn_(maize)___cercospora_leaf_spot gray_leaf_spot": 
                "Remove and destroy infected leaves. Apply fungicides with active ingredients like azoxystrobin, pyraclostrobin, or propiconazole. Rotate crops and improve air circulation.",
            
            "corn_(maize)___common_rust_": 
                "Apply fungicides containing mancozeb, azoxystrobin, or pyraclostrobin. Plant rust-resistant varieties when possible. Ensure proper field drainage.",
            
            "corn_(maize)___northern_leaf_blight": 
                "Remove and destroy infected plant debris. Apply fungicides like azoxystrobin or propiconazole. Use resistant varieties and practice crop rotation.",
            
            # Tomato diseases
            "tomato___bacterial_spot": 
                "Remove infected plant parts and avoid overhead irrigation. Apply copper-based bactericides. Use disease-free seeds and practice crop rotation.",
            
            "tomato___early_blight": 
                "Remove lower infected leaves. Apply fungicides containing chlorothalonil or mancozeb. Ensure proper spacing between plants for air circulation.",
            
            "tomato___late_blight": 
                "This is a serious disease requiring immediate action. Remove infected plants to prevent spread. Apply fungicides with active ingredients like chlorothalonil or mancozeb. Water at the base of plants and avoid overhead irrigation.",
            
            "tomato___leaf_mold": 
                "Improve air circulation and reduce humidity. Apply fungicides containing chlorothalonil or mancozeb. Remove and destroy infected leaves.",
            
            "tomato___septoria_leaf_spot": 
                "Remove infected leaves immediately. Apply fungicides like chlorothalonil or copper-based products. Avoid overhead watering and practice crop rotation.",
            
            "tomato___spider_mites two-spotted_spider_mite": 
                "This is a pest issue. Spray plants with water to dislodge mites. Apply insecticidal soap or neem oil. Introduce predatory mites as biological control.",
            
            "tomato___target_spot": 
                "Remove infected leaves. Apply fungicides containing chlorothalonil. Improve air circulation and avoid overhead irrigation.",
            
            "tomato___tomato_yellow_leaf_curl_virus": 
                "This is a viral disease. No cure exists - remove and destroy infected plants. Control whitefly populations which spread the virus. Use reflective mulches and insect barriers.",
            
            "tomato___tomato_mosaic_virus": 
                "This is a viral disease. Remove and destroy infected plants. Disinfect tools and hands after handling. Use resistant varieties and control aphid populations."
        }
        
        # Convert disease name to lowercase for matching
        disease_key = disease_name.lower().replace(" ", "_")
        
        # Return specific advice if available, otherwise return default
        if disease_key in advice_map:
            return advice_map[disease_key]
        
        return default_advice
    
    @classmethod
    def get_classes(cls):
        """
        Get all available model classes with additional information
        """
        try:
            # Get model loader
            model_loader = cls._get_model_loader()
            
            # Get class names
            class_names = model_loader.get_class_names()
            
            # Transform into structured format with additional info
            result = []
            for idx, class_name in enumerate(class_names):
                # Parse plant type and condition from class name format: "PlantType___Condition"
                parts = class_name.split("___")
                plant_type = parts[0].replace("_", " ")
                condition = parts[1].replace("_", " ") if len(parts) > 1 else "Unknown"
                
                # Create a more readable display name
                display_name = f"{plant_type} - {condition}"
                
                # Get advice for this disease if available
                advice = cls._get_advice_for_disease(class_name)
                
                result.append({
                    "id": idx,
                    "name": class_name,
                    "display_name": display_name,
                    "plant_type": plant_type,
                    "condition": condition,
                    "advice": advice
                })
                
            return result
        except Exception as e:
            logger.error(f"Error retrieving model classes: {str(e)}")
            return []
    
    @classmethod
    def save_prediction_history(cls, prediction_data):
        """
        Save a prediction to the prediction history database
        
        Args:
            prediction_data (dict): Prediction data including metadata
            
        Returns:
            str: ID of the saved prediction or None if saving failed
        """
        try:
            # Save to MongoDB
            prediction_id = PredictionHistory.save_prediction(prediction_data)
            
            if prediction_id:
                logger.info(f"Prediction history saved with ID {prediction_id}")
            else:
                logger.error("Failed to save prediction history")
                
            return prediction_id
        except Exception as e:
            logger.error(f"Error saving prediction history: {str(e)}")
            return None
    
    @classmethod
    def get_user_prediction_history(cls, user_id, limit=20, offset=0):
        """
        Get prediction history for a specific user
        
        Args:
            user_id (str): User ID
            limit (int): Maximum number of results to return
            offset (int): Number of results to skip (for pagination)
            
        Returns:
            list: List of prediction history records
        """
        try:
            return PredictionHistory.get_user_predictions(user_id, limit, offset)
        except Exception as e:
            logger.error(f"Error retrieving prediction history: {str(e)}")
            return []
    
    @classmethod
    def get_prediction_details(cls, prediction_id):
        """
        Get details for a specific prediction
        
        Args:
            prediction_id (str): Prediction ID
            
        Returns:
            dict: Prediction details or None if not found
        """
        try:
            return PredictionHistory.get_prediction_by_id(prediction_id)
        except Exception as e:
            logger.error(f"Error retrieving prediction details: {str(e)}")
            return None
            
    @classmethod
    def get_filtered_predictions(cls, filters=None, sort_by='timestamp', sort_order='desc', limit=100, offset=0):
        """
        Get prediction history with filters
        
        Args:
            filters (dict): Dictionary of filters to apply
            sort_by (str): Field to sort by
            sort_order (str): Sort order ('asc' or 'desc')
            limit (int): Maximum number of results to return
            offset (int): Number of results to skip (for pagination)
            
        Returns:
            list: List of prediction history records
        """
        try:
            return PredictionHistory.get_filtered_predictions(
                filters=filters or {},
                sort_by=sort_by,
                sort_order=sort_order,
                limit=limit,
                offset=offset
            )
        except Exception as e:
            logger.error(f"Error retrieving filtered predictions: {str(e)}")
            return []
            
    @classmethod
    def count_user_predictions(cls, user_id):
        """
        Count total number of predictions for a user
        
        Args:
            user_id (str): User ID
            
        Returns:
            int: Total count of predictions
        """
        try:
            return PredictionHistory.count_user_predictions(user_id)
        except Exception as e:
            logger.error(f"Error counting user predictions: {str(e)}")
            return 0
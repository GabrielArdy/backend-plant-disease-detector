import tensorflow as tf
import numpy as np
import os
import json
from app.utils.log import get_logger
from app.core.resources import ResourceManager
from app.core.models.inference import InferenceModel

# Get logger for this module
logger = get_logger(__name__)

class ModelLoader:
    def __init__(self):
        self.model = InferenceModel()
        self.class_names = []
        
    def load_model(self, model_path=None):
        """Load the saved ML model for inference"""
        try:
            # Get path from resource manager if not provided
            if model_path is None:
                model_path = ResourceManager.get_model_path()
                
            # Load model using the inference model class
            success = self.model.load_model(model_path)
            if not success:
                logger.error("Failed to load model")
                return False
                
            logger.info("Model loaded successfully")
            
            # Try to load class names
            self._load_class_names()
            
            return True
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            return False
    
    def _load_class_names(self):
        """Load class names from the dedicated JSON file"""
        try:
            # Use ResourceManager to load class names
            self.class_names = ResourceManager.load_class_names()
            
            if not self.class_names:
                logger.warning("No class names loaded. Using default class IDs.")
                self.class_names = []
        except Exception as e:
            logger.error(f"Error loading class names: {str(e)}")
            logger.warning("Using default class IDs.")
            # Initialize with empty list
            self.class_names = []
    
    def get_class_names(self):
        """Return the list of all class names available in the model"""
        # If class names were already loaded, return them
        if self.class_names:
            return self.class_names
        
        # If class names not loaded yet, try to load them
        self._load_class_names()
        return self.class_names
    
    def predict(self, preprocessed_image):
        """Make a prediction using the loaded model"""
        if self.model is None:
            raise ValueError("Model not loaded. Call load_model() first.")
        
        # Get raw predictions from the inference model
        predictions = self.model.predict(preprocessed_image)
        
        # Process predictions
        predicted_class = np.argmax(predictions, axis=1)[0]
        confidence = float(predictions[0][predicted_class])
        
        # Map to class name if available
        if len(self.class_names) > predicted_class:
            class_name = self.class_names[predicted_class]
        else:
            class_name = f"class_{predicted_class}"
            
        return {
            "class_id": int(predicted_class),
            "class_name": class_name,
            "confidence": confidence
        }

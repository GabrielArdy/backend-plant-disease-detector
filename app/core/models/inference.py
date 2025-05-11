import tensorflow as tf
import numpy as np
import os
from app.utils.log import get_logger

logger = get_logger(__name__)

class InferenceModel:
    def __init__(self):
        self.model = None
        
    def load_model(self, model_path=None):
        """
        Load a TensorFlow/Keras model for inference
        
        Args:
            model_path: Path to the saved model file (.h5)
            
        Returns:
            True if model loaded successfully, False otherwise
        """
        try:
            # Set default model path if not provided
            if model_path is None:
                # Look in resources directory
                resources_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'resources')
                model_path = os.path.join(resources_dir, 'inference_model.h5')
            
            # Check if model file exists
            if not os.path.exists(model_path):
                logger.error(f"Model file not found at {model_path}")
                return False
            
            # Load the model
            self.model = tf.keras.models.load_model(model_path)
            logger.info(f"Model loaded successfully from {model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            return False
    
    def predict(self, input_data):
        """
        Make a prediction with the loaded model
        
        Args:
            input_data: Input data for prediction (preprocessed image)
            
        Returns:
            Prediction result
        """
        if self.model is None:
            raise ValueError("Model not loaded. Call load_model() first.")
        
        try:
            predictions = self.model.predict(input_data)
            return predictions
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            raise ValueError(f"Prediction failed: {str(e)}")

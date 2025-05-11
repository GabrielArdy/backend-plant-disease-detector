import tensorflow as tf
import os
from app.utils.log import get_logger

logger = get_logger(__name__)

class InferenceModel:
    def __init__(self):
        try:
            # First try the models directory
            if os.path.exists('app/models/inference_model.h5'):
                self.model = tf.keras.models.load_model('app/models/inference_model.h5')
            # Fallback to the model directory
            elif os.path.exists('app/model/inference_model.h5'):
                self.model = tf.keras.models.load_model('app/model/inference_model.h5')
            else:
                logger.error("Model file not found in either app/models/ or app/model/ directories")
                raise FileNotFoundError("Model file not found")
                
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise

    def predict(self, data):
        # Implement the prediction logic
        return self.model.predict(data)

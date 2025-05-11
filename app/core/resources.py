import os
import json
from app.utils.log import get_logger

logger = get_logger(__name__)

class ResourceManager:
    """
    Manager for handling resources like model files and class definitions
    """
    
    @staticmethod
    def get_resources_path():
        """Get the absolute path to the resources directory"""
        return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'resources')
    
    @staticmethod
    def get_model_path():
        """Get the path to the ML model file"""
        # Get from resources directory
        resources_path = ResourceManager.get_resources_path()
        model_path = os.path.join(resources_path, 'inference_model.h5')
        
        if os.path.exists(model_path):
            return model_path
        else:
            logger.error("Model file not found in resources directory")
            return None
            return None
    
    @classmethod
    def load_class_names(cls):
        """Load the class names from JSON file"""
        try:
            # Path to the class names JSON file
            class_file = os.path.join(cls.get_resources_path(), "model_classes.json")
            
            if os.path.exists(class_file):
                with open(class_file, 'r') as f:
                    class_names = json.load(f)
                logger.info(f"Loaded {len(class_names)} class names from {class_file}")
                return class_names
            else:
                logger.warning(f"Class names file not found at {class_file}. Using default class IDs.")
                return []
        except Exception as e:
            logger.error(f"Error loading class names: {str(e)}")
            return []

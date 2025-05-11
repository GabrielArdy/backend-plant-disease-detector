import numpy as np
import io
from PIL import Image
import tensorflow as tf
from app.utils.log import get_logger

logger = get_logger(__name__)

def prep_image(image_file, target_size=(224, 224)):
    """
    Preprocess image for model prediction
    
    Args:
        image_file: Image file object from request.files
        target_size: Target dimensions (height, width) for resizing
        
    Returns:
        Preprocessed image ready for model inference
    """
    try:
        # Read image from file
        image_bytes = image_file.read()
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB (in case of grayscale or RGBA)
        image = image.convert("RGB")
        
        # Resize to target size
        image = image.resize(target_size)
        
        # Convert to numpy array and normalize
        img_array = tf.keras.preprocessing.image.img_to_array(image)
        img_array = img_array / 255.0  # Normalize to [0,1]
        
        # Expand dimensions to create batch of size 1
        img_array = np.expand_dims(img_array, axis=0)
        
        return img_array
    
    except Exception as e:
        logger.error(f"Error preprocessing image: {str(e)}")
        raise ValueError(f"Failed to process image: {str(e)}")
    
    return img_array
# DEPRECATED: Please use app/api/prediction/services.py instead
# This file is kept for reference and backward compatibility

import tensorflow as tf
import numpy as np
from PIL import Image
import io
from app.core.models.model_loader import ModelLoader  # Updated import path
from app.utils.log import get_logger
from app.utils.image import prep_image

# Initialize logger
logger = get_logger(__name__)

# Initialize model loader as a singleton
model_loader = ModelLoader()
model_loader.load_model()

def prep_image(image_file):
    """
    Preprocess the uploaded image file for model prediction
    """
    try:
        # Read image from file
        image_bytes = image_file.read()
        image = Image.open(io.BytesIO(image_bytes))
        
        # Resize image to model's expected dimensions (typically 224x224 for most plant disease models)
        image = image.resize((224, 224))
        
        # Convert to numpy array and normalize
        img_array = tf.keras.preprocessing.image.img_to_array(image)
        img_array = img_array / 255.0  # Normalize to [0,1]
        
        # Add batch dimension
        img_array = np.expand_dims(img_array, axis=0)
        
        return img_array
    
    except Exception as e:
        logger.error(f"Error preprocessing image: {str(e)}")
        raise

def predict_plant_disease(image_file):
    """
    Process the image file and return prediction results
    """
    try:
        # Preprocess the image
        processed_image = prep_image(image_file)
        
        # Get prediction from model
        prediction = model_loader.predict(processed_image)
        
        return prediction
    
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return {
            "error": str(e),
            "class_name": "Unknown",
            "confidence": 0.0
        }

def get_model_classes():
    """
    Get all available class names from the model with additional information
    
    Returns:
        list: List of dictionaries containing class information
    """
    try:
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
            advice = get_advice_for_disease(class_name)
            
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
        logger.error(f"Error getting model classes: {str(e)}")
        return []

def get_advice_for_disease(disease_name):
    """
    Return advice for the detected plant disease
    
    Note: This function uses the legacy hard-coded advice.
    For AI-powered advice, use the advice_service.py module.
    """
    try:
        from app.services.advice_service import get_plant_disease_advice
        
        # Parse the disease name from format: "PlantType___Condition"
        parts = disease_name.split("___")
        plant_type = parts[0].replace("_", " ")
        condition = parts[1].replace("_", " ") if len(parts) > 1 else ""
        
        # Create disease info dictionary for AI advice
        disease_info = {
            'plant_type': plant_type,
            'condition': condition,
            'confidence': 0.9  # Default confidence when not available
        }
        
        # Get AI-powered advice
        advice_data = get_plant_disease_advice(disease_info)
        
        # Format the advice into a single string
        advice = f"TREATMENT: {advice_data['treatment']}\n\n"
        advice += f"PREVENTION: {advice_data['prevention']}\n\n"
        advice += f"ADDITIONAL INFORMATION: {advice_data['additional_info']}"
        
        return advice
    
    except Exception as e:
        logger.error(f"Error getting AI advice: {str(e)}. Falling back to static advice.")
        
        # Simple example - in a real application, this would be more comprehensive
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

import os
import google.generativeai as genai
from app.utils.log import get_logger

# Initialize logger
logger = get_logger(__name__)

def get_advice_for_condition(plant_type, condition):
    """
    Generate structured advice for a plant condition
    
    Args:
        plant_type (str): The type of plant (e.g., "Tomato", "Corn")
        condition (str): The condition or disease (e.g., "Early blight", "Healthy")
        
    Returns:
        dict: Dictionary with structured advice sections
    """
    # Create disease info dictionary
    disease_info = {
        'plant_type': plant_type,
        'condition': condition,
        'confidence': 0.9  # Default confidence when not available
    }
    
    # Get structured advice
    return get_plant_disease_advice(disease_info)

def get_gemini_advice_for_disease(disease_name):
    """
    Generate advice for a plant disease using Gemini AI
    
    This is the function imported by the prediction service
    
    Args:
        disease_name (str): The disease name in the format "PlantType___Condition"
        
    Returns:
        str: Formatted advice text
    """
    try:
        # Parse the disease name
        parts = disease_name.split("___")
        plant_type = parts[0].replace("_", " ")
        condition = parts[1].replace("_", " ") if len(parts) > 1 else ""
        
        # Check if this is a healthy plant
        if "healthy" in condition.lower():
            return "Your plant appears healthy! Continue with regular care and monitoring."
            
        # Create disease info dictionary
        disease_info = {
            'plant_type': plant_type,
            'condition': condition,
            'confidence': 0.9  # Default confidence when not available
        }
        
        # Get AI-powered advice
        advice_data = get_plant_disease_advice(disease_info)
        
        # Format the advice into a single string
        advice = f"TREATMENT:\n{advice_data['treatment']}\n\n"
        advice += f"PREVENTION:\n{advice_data['prevention']}\n\n"
        advice += f"ADDITIONAL INFORMATION:\n{advice_data['additional_info']}"
        
        return advice
        
    except Exception as e:
        logger.error(f"Error generating Gemini advice: {str(e)}")
        return f"Unable to generate AI advice: {str(e)}. Please consult with a plant pathologist for accurate diagnosis and treatment."

# Initialize Gemini API
gemini_available = False
model_name = os.getenv('GENAI_MODEL_NAME', 'gemini-2.0-flash')  # Default to gemini-1.5-pro

try:
    api_key = os.getenv('GENAI_API_KEY')
    
    # Initialize Gemini API with the API key
    if api_key:
        genai.configure(api_key=api_key)
        gemini_available = True
        logger.info(f"Gemini API initialized successfully with model {model_name}")
    else:
        logger.warning("Gemini API key not found in environment variables")
except Exception as e:
    client = None
    logger.error(f"Error initializing Gemini API client: {str(e)}")

def check_gemini_connection():
    """
    Check if the Gemini API is properly configured and working
    
    Returns:
        dict: Connection status information
    """
    status_info = {
        'available': gemini_available,
        'model_name': model_name,
        'error': None
    }
    
    # Skip the check if API key is not configured
    if not gemini_available:
        status_info['error'] = "API key not configured"
        return status_info
        
    try:
        # Try to get available models as a connectivity test
        models = genai.list_models()
        model_found = False
        
        # Check if our configured model is available
        for model in models:
            if model_name in model.name:
                model_found = True
                status_info['model_details'] = {
                    'name': model.name,
                    'display_name': model.display_name,
                    'description': model.description
                }
                break
                
        if not model_found:
            status_info['error'] = f"Configured model {model_name} not found in available models"
            
        return status_info
    except Exception as e:
        logger.error(f"Error checking Gemini connection: {str(e)}")
        status_info['available'] = False
        status_info['error'] = str(e)
        return status_info

def get_plant_disease_advice(disease_info):
    """
    Generate detailed advice for plant disease using Gemini AI
    
    Args:
        disease_info (dict): Dictionary containing information about the disease detection
            - plant_type: Type of plant (e.g., "Tomato", "Corn")
            - condition: Diagnosed condition (e.g., "Early blight", "Common rust")
            - confidence: Confidence score of the prediction
            
    Returns:
        dict: Dictionary containing advice information
            - treatment: Treatment suggestions
            - prevention: Prevention measures
            - additional_info: Additional information about the disease
            - error: Error message if something went wrong
    """
    try:
        if not os.getenv('GENAI_API_KEY'):
            logger.warning("No Gemini API key available. Using fallback advice.")
            return _get_fallback_advice(disease_info)
        
        # Extract plant and disease information
        plant_type = disease_info.get('plant_type', '')
        condition = disease_info.get('condition', '')
        confidence = disease_info.get('confidence', 0)
        
        # Check if the plant is healthy
        if 'healthy' in condition.lower():
            return {
                'treatment': 'No treatment needed.',
                'prevention': 'Continue regular maintenance and monitoring.',
                'additional_info': 'Your plant appears healthy. Continue with proper watering, appropriate sunlight exposure, and regular fertilization as needed for your specific plant type.',
                'error': None
            }
        
        # Create the prompt for the AI
        prompt = _create_plant_disease_prompt(plant_type, condition, confidence)
        
        # Set generation parameters
        generation_config = genai.GenerationConfig(
            temperature=0.2,
            top_p=0.8,
            top_k=40,
            max_output_tokens=1024,
        )
        
        # Generate the content with the Gemini API
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(
            prompt, 
            generation_config=generation_config
        )
        
        # Extract text from response
        response_text = response.text
        
        # Process the AI response
        result = _process_ai_response(response_text)
        
        return result
    
    except Exception as e:
        logger.error(f"Error generating plant disease advice: {str(e)}")
        return {
            'treatment': 'Unable to generate treatment advice.',
            'prevention': 'Unable to generate prevention advice.',
            'additional_info': 'An error occurred when trying to generate advice.',
            'error': str(e)
        }

def _create_plant_disease_prompt(plant_type, condition, confidence):
    """Create a prompt for the AI model"""
    
    prompt = f"""
    You are an expert agricultural scientist specializing in plant diseases and treatment. 
    
    I need detailed advice for a plant disease detected through image analysis:
    - Plant type: {plant_type}
    - Detected condition: {condition}
    - Model confidence: {confidence:.2f} (on a scale of 0 to 1)
    
    Please provide a structured response with the following sections:
    
    1. TREATMENT: Provide specific treatment recommendations for this disease. Include:
       - Organic/natural remedies
       - Chemical treatments (if appropriate)
       - Application methods and frequency
       - When to apply treatments (time of day, weather conditions)
       - How to recognize when treatment is working
    
    2. PREVENTION: How to prevent this disease in the future:
       - Cultural practices
       - Environmental management
       - Preventive treatments
       - Plant selection and resistance
       - Monitoring practices
    
    3. ADDITIONAL INFORMATION: 
       - Disease cause (fungal, bacterial, viral, etc.)
       - Typical progression of the disease
       - Potential impact on crop yield
       - Common misconceptions about this disease
       - Similar diseases that might be confused with this one
    
    Format your response in clear language that a home gardener or small-scale farmer could understand and implement.
    Be specific about treatments, including proper dosages and application methods.
    Ensure that chemical treatments mentioned include both active ingredient names and common commercial product names when applicable.
    """
    
    # Using the new content generation approach with structured prompting
    return prompt

def _process_ai_response(response_text):
    """Process the AI response text into a structured format"""
    
    # Initialize result structure
    result = {
        'treatment': '',
        'prevention': '',
        'additional_info': '',
        'error': None
    }
    
    try:
        # More robust section parsing
        import re
        
        # Define section patterns
        section_patterns = {
            'treatment': [
                r'(?i)^\s*TREATMENT:',
                r'(?i)^\s*1\.\s*TREATMENT',
                r'(?i)^\s*1\.\s*TREAT'
            ],
            'prevention': [
                r'(?i)^\s*PREVENTION:',
                r'(?i)^\s*2\.\s*PREVENTION',
                r'(?i)^\s*2\.\s*PREVENT'
            ],
            'additional_info': [
                r'(?i)^\s*ADDITIONAL\s+INFORMATION:',
                r'(?i)^\s*3\.\s*ADDITIONAL\s+INFORMATION',
                r'(?i)^\s*ADDITIONAL\s+INFO'
            ]
        }
        
        # Process response by lines
        sections = response_text.split('\n')
        current_section = None
        
        for line in sections:
            line = line.strip()
            
            if not line:
                continue
            
            # Check if this line starts a new section
            new_section_found = False
            for section, patterns in section_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, line):
                        current_section = section
                        new_section_found = True
                        break
                if new_section_found:
                    break
                    
            # If this is a section header, skip adding it to content
            if new_section_found:
                continue
                
            # Add content to the current section
            if current_section and line:
                result[current_section] += line + "\n"
        
        # Clean up extra whitespace
        for key in result:
            if isinstance(result[key], str):
                result[key] = result[key].strip()
        
        # If any section is empty, provide a generic message
        if not result['treatment']:
            result['treatment'] = "No specific treatment information was generated."
            
        if not result['prevention']:
            result['prevention'] = "No prevention information was generated."
            
        if not result['additional_info']:
            result['additional_info'] = "No additional information was provided."
        
        # Add metadata
        from datetime import datetime
        result['generated_at'] = datetime.utcnow().isoformat()
        result['model_used'] = model_name
            
    except Exception as e:
        logger.error(f"Error processing AI response: {str(e)}")
        result['error'] = f"Error processing advice: {str(e)}"
        
    return result

def _get_fallback_advice(disease_info):
    """Generate fallback advice when Gemini API is not available"""
    
    plant_type = disease_info.get('plant_type', '').lower()
    condition = disease_info.get('condition', '').lower()
    
    # Check if plant is healthy
    if 'healthy' in condition:
        return {
            'treatment': 'No treatment needed.',
            'prevention': 'Continue regular maintenance and monitoring.',
            'additional_info': 'Your plant appears healthy. Continue with proper watering, appropriate sunlight exposure, and regular fertilization as needed for your specific plant type.',
            'error': None
        }
    
    # Basic fallback advice
    basic_advice = {
        'corn': {
            'general': {
                'treatment': 'Remove infected plant parts. Apply appropriate fungicide based on specific disease. Ensure proper spacing for air circulation.',
                'prevention': 'Practice crop rotation. Use disease-resistant varieties. Avoid overhead irrigation.',
                'additional_info': 'Corn diseases are often fungal in nature and spread during warm, humid conditions.'
            },
            'cercospora': {
                'treatment': 'Apply fungicides with active ingredients like azoxystrobin, pyraclostrobin, or propiconazole. Remove severely infected leaves.',
                'prevention': 'Practice crop rotation with non-host crops. Improve air circulation. Manage field residues.',
                'additional_info': 'Gray leaf spot is caused by the fungus Cercospora zeae-maydis and thrives in humid conditions.'
            },
            'rust': {
                'treatment': 'Apply fungicides containing mancozeb, azoxystrobin, or pyraclostrobin at first sign of infection.',
                'prevention': 'Plant rust-resistant varieties. Ensure proper field drainage. Monitor fields regularly.',
                'additional_info': 'Common rust is caused by Puccinia sorghi fungus and appears as small, circular pustules on leaves.'
            },
            'blight': {
                'treatment': 'Apply fungicides like azoxystrobin or propiconazole. Remove infected plant debris.',
                'prevention': 'Use resistant varieties. Practice crop rotation. Maintain field hygiene.',
                'additional_info': 'Northern leaf blight is caused by Exserohilum turcicum fungus and appears as long, elliptical lesions on leaves.'
            }
        },
        'tomato': {
            'general': {
                'treatment': 'Remove infected plant parts. Apply appropriate fungicide or bactericide based on specific disease. Ensure proper spacing and pruning.',
                'prevention': 'Use disease-resistant varieties. Practice crop rotation. Water at the base of plants.',
                'additional_info': 'Tomato plants are susceptible to various fungal, bacterial, and viral diseases.'
            },
            'spot': {
                'treatment': 'Apply copper-based bactericides. Remove infected leaves. Increase air circulation.',
                'prevention': 'Use disease-free seeds. Avoid overhead irrigation. Sterilize garden tools.',
                'additional_info': 'Bacterial spot is caused by Xanthomonas bacteria and thrives in warm, wet conditions.'
            },
            'blight': {
                'treatment': 'Apply fungicides containing chlorothalonil or mancozeb. Remove infected leaves immediately.',
                'prevention': 'Proper plant spacing for good air circulation. Mulch around plants. Water at the base.',
                'additional_info': 'Early blight (Alternaria solani) and late blight (Phytophthora infestans) are serious fungal diseases that can destroy crops.'
            },
            'virus': {
                'treatment': 'No cure exists for viral diseases. Remove and destroy infected plants to prevent spread.',
                'prevention': 'Control insect vectors like aphids and whiteflies. Use reflective mulches. Plant resistant varieties.',
                'additional_info': 'Viral diseases like Tomato Yellow Leaf Curl Virus and Tomato Mosaic Virus are spread by insects and cannot be cured once a plant is infected.'
            }
        }
    }
    
    # Select the most relevant advice
    if plant_type in basic_advice:
        plant_advice = basic_advice[plant_type]
        
        # Try to find specific condition advice
        condition_key = next((k for k in plant_advice.keys() if k in condition), 'general')
        advice = plant_advice[condition_key]
        
        return {
            'treatment': advice['treatment'],
            'prevention': advice['prevention'],
            'additional_info': advice['additional_info'],
            'error': 'Using fallback advice (Gemini API not available)'
        }
    
    # Default generic advice
    return {
        'treatment': 'Remove infected plant parts. Apply appropriate treatments based on disease type (fungal, bacterial, or viral).',
        'prevention': 'Practice crop rotation. Maintain proper plant spacing. Water at the base of plants.',
        'additional_info': 'Consult with a local agricultural extension office for specific advice on this plant disease.',
        'error': 'Using generic fallback advice (Gemini API not available)'
    }
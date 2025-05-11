from flask import request, jsonify, current_app
from app.api.prediction import prediction_bp
from app.api.prediction.services import PredictionService
from app.utils.generators import generate_uuid, get_current_timestamp
from app.utils.log import get_logger
from app.utils.storage import ImageStorage
from app.core.models.model_loader import ModelLoader

logger = get_logger(__name__)

@prediction_bp.route('/predict', methods=['POST'])
def predict():
    """
    Predict plant disease from uploaded image and save to history
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    user_id = request.form.get('user_id', '')
    save_image = request.form.get('save_image', 'true').lower() == 'true'
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    try:
        # Generate unique ID for this prediction
        prediction_id = generate_uuid()
        timestamp = get_current_timestamp()
        
        # Process prediction
        result = PredictionService.predict_disease(file, user_id)
        
        # Add metadata to result
        result['prediction_id'] = prediction_id
        result['timestamp'] = timestamp
        result['user_id'] = user_id
        
        # Save image if requested
        if save_image:
            # Create a copy of the file since we've already read it for prediction
            file.seek(0)
            image_path = ImageStorage.save_prediction_image(file, prediction_id, user_id)
            if image_path:
                result['image_path'] = image_path
                
        # Save prediction to history
        PredictionService.save_prediction_history(result)
        
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@prediction_bp.route('/classes', methods=['GET'])
def get_classes():
    """
    Get all available classes for prediction
    """
    try:
        classes = PredictionService.get_classes()
        return jsonify({'classes': classes}), 200
    except Exception as e:
        logger.error(f"Error retrieving classes: {str(e)}")
        return jsonify({'error': str(e)}), 500

@prediction_bp.route('/history', methods=['GET'])
def get_prediction_history():
    """
    Get prediction history for a specific user
    
    Required query parameters:
    - user_id: ID of the user whose history to retrieve
    
    Optional query parameters:
    - limit: Maximum number of records to return (default 20)
    - offset: Number of records to skip for pagination (default 0)
    """
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    
    try:
        # Get pagination parameters
        limit = int(request.args.get('limit', 20))
        offset = int(request.args.get('offset', 0))
        
        # Validate parameters
        if limit < 1 or limit > 100:
            limit = 20
        if offset < 0:
            offset = 0
            
        # Get prediction history
        history = PredictionService.get_user_prediction_history(user_id, limit, offset)
        
        return jsonify({
            'user_id': user_id,
            'predictions': history,
            'count': len(history),
            'limit': limit,
            'offset': offset
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving prediction history: {str(e)}")
        return jsonify({'error': str(e)}), 500

@prediction_bp.route('/history/<prediction_id>', methods=['GET'])
def get_prediction_detail(prediction_id):
    """
    Get details for a specific prediction
    
    Path parameters:
    - prediction_id: ID of the prediction to retrieve
    
    Query parameters:
    - include_image: Set to 'true' to include base64 encoded image data (default: false)
    """
    include_image = request.args.get('include_image', 'false').lower() == 'true'
    
    try:
        prediction = PredictionService.get_prediction_details(prediction_id)
        
        if prediction:
            # Add image data if requested and available
            if include_image and 'image_path' in prediction and prediction['image_path']:
                image_data = ImageStorage.get_image_as_base64(prediction['image_path'])
                if image_data:
                    prediction['image_data'] = image_data
                    
            return jsonify(prediction), 200
        else:
            return jsonify({'error': 'Prediction not found'}), 404
            
    except Exception as e:
        logger.error(f"Error retrieving prediction details: {str(e)}")
        return jsonify({'error': str(e)}), 500
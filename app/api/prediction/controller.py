from flask import request, jsonify, current_app, g
from app.api.prediction import prediction_bp
from app.api.prediction.services import PredictionService
from app.utils.generators import generate_uuid, get_current_timestamp
from app.utils.log import get_logger
from app.utils.storage import ImageStorage
from app.core.models.model_loader import ModelLoader
from app.middleware.auth import token_required

logger = get_logger(__name__)

@prediction_bp.route('/predict', methods=['POST'])
@token_required
def predict():
    """
    Predict plant disease from uploaded image and save to history
    Requires authentication
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    # Get user_id from authentication token
    user_id = g.user_id
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
@token_required
def get_prediction_history():
    """
    Get prediction history for the authenticated user
    
    Optional query parameters:
    - limit: Maximum number of records to return (default 20)
    - offset: Number of records to skip for pagination (default 0)
    """
    # Get user_id from authentication token
    user_id = g.user_id
    
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
@token_required
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

@prediction_bp.route('/my-predictions', methods=['GET'])
@token_required
def get_all_user_predictions():
    """
    Get all prediction histories for the authenticated user
    
    Optional query parameters:
    - limit: Maximum number of records to return (default 100)
    - offset: Number of records to skip for pagination (default 0)
    - sort_by: Field to sort by (default 'timestamp')
    - sort_order: Sort order ('asc' or 'desc', default 'desc')
    - plant_type: Filter by plant type
    - condition: Filter by plant condition (e.g., 'healthy', 'late_blight')
    """
    user_id = g.user_id
    
    try:
        # Get pagination and filter parameters
        limit = min(int(request.args.get('limit', 100)), 500)
        offset = int(request.args.get('offset', 0))
        sort_by = request.args.get('sort_by', 'timestamp')
        sort_order = request.args.get('sort_order', 'desc').lower()
        plant_type = request.args.get('plant_type', None)
        condition = request.args.get('condition', None)
        
        # Validate sort order
        if sort_order not in ['asc', 'desc']:
            sort_order = 'desc'
        
        # Prepare filters
        filters = {'user_id': user_id}
        if plant_type:
            filters['plant_type'] = plant_type
        if condition:
            filters['condition'] = condition
            
        # Get predictions with filters
        predictions = PredictionService.get_filtered_predictions(
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=limit,
            offset=offset
        )
        
        # Get total count of user's predictions
        total_count = PredictionService.count_user_predictions(user_id)
        
        return jsonify({
            'user_id': user_id,
            'predictions': predictions,
            'count': len(predictions),
            'total': total_count,
            'limit': limit,
            'offset': offset
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving all user predictions: {str(e)}")
        return jsonify({'error': str(e)}), 500
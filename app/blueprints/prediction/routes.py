from flask import jsonify, request
from . import prediction_bp
from .services import predict_disease

@prediction_bp.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    result = predict_disease(data)
    return jsonify(result)

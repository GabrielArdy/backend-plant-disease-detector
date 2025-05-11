# This file makes the api directory a Python package
from app.api.auth import auth_bp
from app.api.prediction import prediction_bp

__all__ = ['auth_bp', 'prediction_bp']

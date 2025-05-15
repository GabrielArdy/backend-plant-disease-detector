#!/usr/bin/env python
# filepath: /home/ardy/plant-disease/backend/app/api/health/controller.py

from flask import Blueprint, jsonify
from app.extensions import mongo, fs
from app.services.advice_service import AdviceService

health_bp = Blueprint("health", __name__, url_prefix="/api")

@health_bp.route("/health", methods=["GET"])
def health_check():
    """
    Simple health check endpoint to verify API is working
    ---
    responses:
        200:
            description: Server is healthy
    """
    # Check MongoDB connection
    mongo_status = False
    gridfs_status = False
    advice_status = False
    
    try:
        # Test MongoDB connection
        mongo_status = mongo.db.command('ping').get('ok', 0) == 1.0
        
        # Test GridFS connection
        fs._ensure_initialized()  # Make sure GridFS is initialized
        gridfs_status = True
        
        # Test advice service
        advice_service = AdviceService()
        advice_status = advice_service.is_available()
    except Exception as e:
        pass
    
    status = {
        "status": "healthy" if all([mongo_status, gridfs_status, advice_status]) else "degraded",
        "services": {
            "mongodb": "ok" if mongo_status else "error",
            "gridfs": "ok" if gridfs_status else "error",
            "advice_service": "ok" if advice_status else "error"
        }
    }
    
    return jsonify(status)

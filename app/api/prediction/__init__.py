# This file makes the prediction directory a Python package
from flask import Blueprint

prediction_bp = Blueprint('prediction', __name__, url_prefix='/api/prediction')

from app.api.prediction import controller

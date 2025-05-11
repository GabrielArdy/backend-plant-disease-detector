# This file makes the auth directory a Python package
from flask import Blueprint

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

from app.api.auth import controller

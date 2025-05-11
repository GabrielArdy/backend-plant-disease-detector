# DEPRECATED: Please use app/api/auth/models.py for Auth and Profile models
# and app/core/models/inference.py for inference models
# This file is kept for backward compatibility

from app.api.auth.models import Auth, Profile
from app.core.models.inference import InferenceModel

__all__ = ['Auth', 'Profile', 'InferenceModel']

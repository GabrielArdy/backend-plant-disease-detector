import uuid
from datetime import datetime

def generate_uuid():
    """Generate a unique identifier"""
    return str(uuid.uuid4())

def get_current_timestamp():
    """Get the current timestamp in ISO format"""
    return datetime.now().isoformat()

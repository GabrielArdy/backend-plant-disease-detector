# API Directory Structure

This directory contains the API routes, controllers, and services organized by feature modules.

## Directory Structure

```
api/
├── __init__.py           # Package initialization
├── auth/                 # Authentication module
│   ├── __init__.py       # Blueprint definition
│   ├── controller.py     # Route handlers
│   ├── models.py         # Data models
│   └── services.py       # Business logic
└── prediction/           # Prediction module
    ├── __init__.py       # Blueprint definition
    ├── controller.py     # Route handlers
    └── services.py       # Business logic
```

## Adding a New Feature Module

To add a new feature module:

1. Create a new directory for your feature (e.g., `user/`)
2. Create the following files:
   - `__init__.py` - Define your Blueprint with appropriate URL prefix
   - `controller.py` - Route handlers
   - `models.py` - (Optional) Data models if needed
   - `services.py` - Business logic

3. Register your Blueprint in `app/__init__.py`

Example of a new module `__init__.py`:

```python
from flask import Blueprint

feature_bp = Blueprint('feature', __name__, url_prefix='/api/feature')

from app.api.feature import controller
```

## Best Practices

- Keep controller methods thin, delegating logic to services
- Place data models in the `models.py` file
- Handle business logic in services
- Use consistent error handling and response formatting

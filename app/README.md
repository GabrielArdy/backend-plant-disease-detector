# Plant Disease API - Code Structure

This directory contains the main application code organized in a clean, modular architecture.

## Directory Structure

```
app/
  ├── __init__.py         # Application factory
  ├── config.py           # Configuration settings
  ├── extensions.py       # Flask extensions (MongoDB, Bcrypt, CORS)
  │
  ├── api/                # API endpoints organized by domain
  │   ├── __init__.py     # API blueprint registration
  │   ├── README.md       # Documentation for API structure
  │   ├── auth/           # Authentication endpoints
  │   │   ├── __init__.py
  │   │   ├── controller.py  # Route handlers
  │   │   ├── models.py     # Auth and Profile models
  │   │   └── services.py   # Auth business logic
  │   │
  │   └── prediction/     # Disease prediction endpoints
  │       ├── __init__.py
  │       ├── controller.py  # Route handlers
  │       └── services.py    # Prediction business logic
  │
  ├── core/               # Core application functionality
  │   ├── __init__.py
  │   ├── README.md       # Documentation for core structure
  │   ├── resources.py    # Resource manager
  │   └── models/         # ML models and loaders
  │       ├── __init__.py
  │       ├── inference.py    # Base inference model
  │       └── model_loader.py # Model loading utilities
  │
  ├── db/                 # Database operations
  │   ├── __init__.py
  │   └── mongo.py        # MongoDB initialization
  │
  ├── resources/          # Static resources
  │   ├── __init__.py
  │   ├── inference_model.h5  # ML model file
  │   └── model_classes.json  # Class definitions for ML model
  │
  └── utils/              # Utility functions
      ├── __init__.py
      ├── generators.py   # ID and timestamp generators
      ├── image.py        # Image processing utilities
      └── log.py          # Logging utilities
```

## Key Components

1. **API Layer (`/api`)**: 
   - Contains HTTP endpoints organized by domain (auth, prediction)
   - Each domain has its controllers (route handlers) and services (business logic)

2. **Core Layer (`/core`)**: 
   - Contains domain-independent business logic
   - ML model loading and inference is handled here
   - Resource management for model files and class definitions

3. **Database Layer (`/db`)**: 
   - MongoDB initialization and collection setup
   - Database indexes and constraints

4. **Resources (`/resources`)**: 
   - Static resources like ML model files and class definitions

5. **Utilities (`/utils`)**: 
   - Helper functions used across the application

## Architecture Principles

1. **Separation of Concerns**: 
   - Controllers handle HTTP I/O
   - Services handle business logic
   - Models handle data access

2. **Dependency Inversion**: 
   - Higher-level modules depend on abstractions, not implementations
   - ML model loader depends on abstract interfaces

3. **Single Responsibility**: 
   - Each module has a specific responsibility
   - Classes are focused on doing one thing well

## Deprecated Directories

The following directories are deprecated and kept only for backward compatibility:
- `/blueprints` - Replaced by `/api`
- `/controller` and `/controllers` - Replaced by `/api/{module}/controller.py`
- `/model` and `/models` - Replaced by `/core/models` and `/api/{module}/models.py`
- `/routes` - Replaced by `/api`
- `/services` - Replaced by `/api/{module}/services.py`

New development should follow the new directory structure.

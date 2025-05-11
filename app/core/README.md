# Core Directory

This directory contains the core functionality of the application, including model handling and inference.

## Directory Structure

```
core/
├── __init__.py           # Package initialization
├── resources.py          # Resource management utilities
└── models/               # ML model functionality
    ├── __init__.py       # Package initialization
    ├── inference.py      # Model inference logic
    └── model_loader.py   # Model loading utilities
```

## Components

### ResourceManager

The `ResourceManager` class in `resources.py` provides a centralized way to access application resources such as model files and class definitions.

### Models

The `models` directory contains classes for handling machine learning models:

- `InferenceModel`: Handles model prediction and preprocessing
- `ModelLoader`: Manages loading models and their associated metadata

## Usage

```python
from app.core.models.model_loader import ModelLoader

# Initialize model loader
model_loader = ModelLoader()
model_loader.load_model()

# Make a prediction
predictions = model_loader.predict(preprocessed_image)
```

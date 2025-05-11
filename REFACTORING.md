# Plant Disease API Refactoring

This document summarizes the refactoring work done on the Plant Disease API to create a cleaner architecture.

## Overview of Changes

### 1. Created New Directory Structure

- **API Layer (`/app/api/`)**: 
  - Organized endpoints by domain (auth, prediction)
  - Each domain has its own controller, services, and models
  - Added clear blueprint definitions with proper URL prefixes

- **Core Layer (`/app/core/`)**: 
  - Centralized model loading and inference
  - Added resource management utilities
  - Improved model handling with better error reporting

- **Resources (`/app/resources/`)**: 
  - Centralized all model files and class definitions
  - Eliminated duplicates from multiple directories

### 2. Removed Redundant Directories

The following directories have been completely removed as part of the refactoring:
- `/app/blueprints/` → `/app/api/`
- `/app/controller/` and `/app/controllers/` → `/app/api/{module}/controller.py`
- `/app/model/` and `/app/models/` → `/app/core/models/` and `/app/api/{module}/models.py`
- `/app/routes/` → `/app/api/`
- `/app/services/` → `/app/api/{module}/services.py`

### 3. Improved Code Organization

- **Modular Structure**: Clear separation by domain/feature
- **Better Imports**: Updated all import statements to reflect new structure
- **Enhanced Error Handling**: Improved try/except blocks with proper logging
- **Documentation**: Added README files explaining the new architecture

### 4. Model Handling Improvements

- **ResourceManager**: Centralized resource file access
- **InferenceModel**: Separated model loading from inference
- **ModelLoader**: Enhanced with better error handling and validation
- **Image Processing**: Improved image preprocessing utilities

## Migration Guide

For developers working with this codebase:

1. Use the new directory structure for all new features:
   - New APIs should be added under `/app/api/{domain}/`
   - New models should be added to the appropriate domain

2. Refer to the README.md files in each directory for guidance:
   - `/app/api/README.md` for API structure
   - `/app/core/README.md` for core functionality

3. Avoid using the deprecated directories, which are kept only for backward compatibility.

## Testing

Make sure to test the following functionality after this refactoring:
- Authentication and user profile handling
- Plant disease prediction with image uploads
- Class listing and disease information retrieval

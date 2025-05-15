# Plant Disease API Backend

This is a Flask-based backend for the Plant Disease Detection application with MongoDB integration for user authentication, profile management, and GridFS-based image storage.

## Project Structure

```
backend/
    app/
        __init__.py                # Application factory
        config.py                  # Configuration settings
        extensions.py              # Flask extensions (MongoDB, Bcrypt, CORS)
        api/                       # API endpoints by domain
            auth/                  # Authentication domain
                controller.py      # Auth route handlers
                models.py          # User and profile models
                services.py        # Auth business logic
            prediction/            # Prediction domain
                controller.py      # Prediction route handlers
                services.py        # Prediction business logic
        core/                      # Core functionality
            models/                # ML model handling
                inference.py       # Model inference
                model_loader.py    # Model loading utilities
            resources.py           # Resource management
        db/
            mongo.py               # MongoDB initialization
        utils/
            log.py                 # Logging utilities
            image.py               # Image processing utilities
            generators.py          # ID and timestamp generators
        resources/
            model_classes.json     # Classes for prediction
            inference_model.h5     # ML model file
    logs/
        plant_disease.log          # Application logs
    tests/
        test_mongo_connection.py   # Test MongoDB connection
        test_auth_api.py           # Test authentication API
    requirements.txt               # Project dependencies
    run.py                         # Application entry point
```

## Requirements

- Python 3.8+
- MongoDB 4.4+
- TensorFlow 2.x
- (Optional) CUDA and cuDNN for GPU acceleration

## Setup Instructions

### 1. Install MongoDB

**Ubuntu/Debian:**
```bash
# Install MongoDB
sudo apt update
sudo apt install -y mongodb

# Start MongoDB service
sudo systemctl start mongodb
sudo systemctl enable mongodb
```

**macOS:**
```bash
# Using Homebrew
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

### 2. Create a Python virtual environment and install dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Run the Application

```bash
# Set environment variables (optional)
export FLASK_ENV=development
export MONGO_URI=mongodb://localhost:27017/plant_disease_dev
export SECRET_KEY=your_secret_key

# Run the application
python run.py
```

The API will be available at http://localhost:5000.

## GPU Support

The application automatically detects if a GPU is available and uses it to accelerate disease detection processing. For details on the GPU configuration, see [GPU Configuration Guide](docs/gpu_configuration.md).

To check if your system is using GPU acceleration, visit the endpoint:
```
GET /api/prediction/system-info
```

## Quick Start for Development

We've provided a convenience script for local development:

```bash
# Make the script executable (if not already)
chmod +x start_dev.sh

# Run the development script
./start_dev.sh
```

This script:
1. Checks if MongoDB is running and starts it if needed
2. Sets the required environment variables (including Gemini API key)
3. Activates the virtual environment if present
4. Starts the Flask application

### Default Demo Account

When running in development mode, a demo account is automatically created:
- Username: `demo`
- Password: `demo123` 

You can use these credentials for testing the API.

## Docker Setup

This project includes Docker configuration for easy setup and deployment.

### Using Docker Compose

1. Make sure Docker and Docker Compose are installed on your system.
2. Run the application stack:

```bash
docker-compose up
```

This will start both MongoDB and the Flask application.

### Building and Running the Docker Image Manually

1. Build the Docker image:
```bash
docker build -t plant-disease-api .
```

2. Run MongoDB:
```bash
docker run -d --name mongodb -p 27017:27017 mongo
```

3. Run the application:
```bash
docker run -d --name plant-disease-api -p 5000:5000 \
  --link mongodb \
  -e MONGO_URI=mongodb://mongodb:27017/plant_disease_dev \
  -e FLASK_ENV=development \
  -e SECRET_KEY=your_secret_key \
  plant-disease-api
```

The API will be available at http://localhost:5000.

## MongoDB Admin Interface

The Docker setup includes MongoDB Express, a web-based MongoDB admin interface that makes it easy to manage your MongoDB database.

When running with Docker Compose, MongoDB Express is available at:
```
http://localhost:8081
```

This provides a convenient way to:
- View and create databases
- Manage collections
- Create and edit documents
- Import and export data
- Run queries

This is particularly useful for:
1. Verifying user registration worked correctly
2. Checking profile data is being saved
3. Debugging authentication issues

## API Endpoints

### Authentication

- `POST /api/auth/register` - Register a new user
  - Request body: `{ "first_name": "...", "last_name": "...", "email": "...", "username": "...", "password": "..." }`

- `POST /api/auth/login` - Login a user
  - Request body: `{ "username": "...", "password": "..." }`

- `GET /api/auth/profile` - Get user profile (requires authentication)
  - Headers: `Authorization: Bearer {token}`

- `PUT /api/auth/profile` - Update user profile (requires authentication)
  - Headers: `Authorization: Bearer {token}`
  - Request body: `{ "avatar": "...", "cover_image": "...", "description": "..." }`

### System Health

- `GET /api/health` - Check the health status of system components
  - Response includes status of MongoDB, GridFS, and Advice Service
  - No authentication required
  - Example response:
    ```json
    {
      "status": "healthy",
      "services": {
        "mongodb": "ok",
        "gridfs": "ok",
        "advice_service": "ok"
      }
    }
    ```

### Prediction

- `POST /api/prediction/predict` - Predict plant disease from image (requires authentication)
  - Headers: `Authorization: Bearer {token}`
  - Request body: Multipart form with:
    - `file`: Image file
    - `save_image`: Boolean to save image (optional, default: true)
  - Response includes AI-generated advice about treatment, prevention, and additional information for the detected disease
  
- `POST /api/prediction/advice` - Get AI-powered advice for a specific plant disease (requires authentication)
  - Headers: 
    - `Authorization: Bearer {token}`
    - `Content-Type: application/json`
  - Request body: `{ "plant_type": "...", "condition": "..." }`
  - Response includes structured advice with treatment, prevention, and additional information sections
  
- `GET /api/prediction/classes` - Get all available disease classes
  
- `GET /api/prediction/history` - Get prediction history for the authenticated user (requires authentication)
  - Headers: `Authorization: Bearer {token}`
  - Query parameters:
    - `limit`: Maximum number of records to return (optional, default: 20)
    - `offset`: Number of records to skip for pagination (optional, default: 0)
  
- `GET /api/prediction/history/{prediction_id}` - Get details for a specific prediction (requires authentication)
  - Headers: `Authorization: Bearer {token}`
  - Path parameters:
    - `prediction_id`: ID of the prediction to retrieve
  - Query parameters:
    - `include_image`: Include base64 encoded image data (optional, default: false)
  
- `GET /api/prediction/my-predictions` - Get all prediction histories for the authenticated user with filtering (requires authentication)
  - Headers: `Authorization: Bearer {token}`
  - Query parameters:
    - `limit`: Maximum number of records to return (optional, default: 100)
    - `offset`: Number of records to skip for pagination (optional, default: 0)
    - `sort_by`: Field to sort by (optional, default: 'timestamp')
    - `sort_order`: Sort order ('asc' or 'desc', optional, default: 'desc')
    - `plant_type`: Filter by plant type (optional)
    - `condition`: Filter by plant condition (optional)

## AI-Powered Plant Disease Advice

The system uses Google's Gemini AI to generate detailed advice for plant diseases. When a disease is detected, the API automatically provides structured advice with:

- **Treatment recommendations**: Specific methods to treat the current infection
- **Prevention strategies**: Ways to prevent future occurrences
- **Additional information**: Background on the disease, causes, and impact

See the [AI Advice Documentation](docs/ai_advice.md) for more details on this feature.

## Image Storage with GridFS

The system uses MongoDB's GridFS for storing plant disease images. This provides several benefits:

- Images are stored directly in the MongoDB database for easier management
- File metadata is stored alongside the images for better organization
- No need to manage file system directories and permissions

The system also maintains backward compatibility with the older file system-based storage. For more details, see the [GridFS Storage Documentation](docs/gridfs_storage.md).

A migration script is included to help move existing images from the file system to GridFS:

```bash
# Check what would be migrated without making changes
python scripts/migrate_to_gridfs.py --dry-run

# Run the actual migration
python scripts/migrate_to_gridfs.py
```

## Recent Updates (May 15, 2025)

### 1. Fixed GridFS Storage Issue

We've fixed an issue with GridFS storage where a `'NoneType' object has no attribute 'put'` error would occur. The solution includes:

- Implemented a `GridFSProxy` class in `extensions.py` that lazily initializes GridFS only when needed
- Ensured proper initialization within Flask app context
- Added improved error handling for GridFS operations
- Fixed application startup by properly initializing GridFS
- Added comprehensive tests for GridFS functionality

### 2. Enhanced Advice Generation for Plant Diseases

We've improved the advice generation system, particularly for Tomato Early Blight where it was returning empty or placeholder text:

- Enhanced the `_process_ai_response()` function to better parse AI-generated responses
- Added multiple section header patterns for more robust content extraction
- Implemented fallback parsing for cases where strict pattern matching fails
- Added specific hardcoded fallback advice for common conditions like Tomato Early Blight
- Fixed logging issues and improved debugging capabilities

### 3. Added Health Monitoring

- Added a new `/api/health` endpoint to monitor system status
- Provides real-time checks of MongoDB, GridFS, and Advice Service
- Helps quickly identify if any component is not functioning properly

### How to Test These Fixes

```bash
# Test GridFS functionality
python test_fixed_gridfs.py

# Test advice generation
python test_advice.py

# Verify all systems are working
python verify_fixes.py

# Update any existing bad advice in the database
python fix_tomato_advice.py
```

## API Testing with Postman

A Postman collection is included in the repository to help with testing the API:

1. Import the `postman_collection.json` file into Postman
2. Create an environment with a `base_url` variable set to `http://localhost:5000`
3. The collection includes scripts that automatically save the authentication token

The collection includes endpoints for:
- User registration
- Login
- Profile management
- Disease prediction
- AI-powered plant disease advice

## Testing

To test the MongoDB connection:
```bash
python -m tests.test_mongo_connection
```

To test the authentication API (server must be running):
```bash
python -m tests.test_auth_api
```

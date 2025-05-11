# Plant Disease API Backend

This is a Flask-based backend for the Plant Disease Detection application with MongoDB integration for user authentication and profile management.

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
2. Sets the required environment variables
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

### Prediction

- `POST /api/prediction/predict` - Predict plant disease from image
  - Request body: Image data

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

## Testing

To test the MongoDB connection:
```bash
python -m tests.test_mongo_connection
```

To test the authentication API (server must be running):
```bash
python -m tests.test_auth_api
```

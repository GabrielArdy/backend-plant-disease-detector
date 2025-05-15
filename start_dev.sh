#!/bin/bash
# filepath: /home/ardy/plant-disease/backend/start_dev.sh

# Check if MongoDB is running
echo "Checking MongoDB service..."
if systemctl is-active --quiet mongodb || systemctl is-active --quiet mongod; then
    echo "MongoDB service is running"
else
    echo "MongoDB service is not running. Starting MongoDB..."
    sudo systemctl start mongodb || sudo systemctl start mongod
    
    if [ $? -ne 0 ]; then
        echo "Failed to start MongoDB service."
        echo "You can use Docker to run MongoDB instead:"
        echo "docker run -d --name mongodb -p 27017:27017 mongo"
        exit 1
    fi
fi

# Set environment variables
export FLASK_ENV=development
export MONGO_URI=mongodb://localhost:27017/plant_disease_dev
export SECRET_KEY=development_secret_key
export JWT_SECRET_KEY=jwt_secret_key_for_dev

# Set Gemini API environment variables
export GENAI_API_KEY=AIzaSyAl4gK3sb17rbTZL9FwF-59ZuOEFTqhKVM
export GENAI_PROJECT_ID=167152973650
export GENAI_LOCATION=global
export GENAI_MODEL_NAME=gemini-2.0-flash

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Start the Flask application
echo "Starting Flask application..."
python run.py

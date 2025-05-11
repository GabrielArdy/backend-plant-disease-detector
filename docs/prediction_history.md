# Prediction History Feature

This document explains how to use the prediction history feature in the Plant Disease API.

## Overview

The prediction history feature allows you to:

1. Save predictions to MongoDB for future reference
2. Associate predictions with specific users
3. Store and retrieve the images used for predictions
4. Query prediction history by user

## API Endpoints

### Make a Prediction and Save to History

**Endpoint:** `POST /api/prediction/predict`

**Form Parameters:**
- `file`: The image file to analyze (required)
- `user_id`: ID of the user making the prediction (optional)
- `save_image`: Whether to save the image file (default: true)

**Example Request:**
```bash
curl -X POST http://localhost:5000/api/prediction/predict \
  -F "file=@plant_image.jpg" \
  -F "user_id=12345678"
```

**Example Response:**
```json
{
  "class_id": 3,
  "class_name": "Corn_(maize)___healthy",
  "confidence": 0.92,
  "prediction_id": "8a7b6c5d-4e3f-2g1h-0i9j-8k7l6m5n4o3p",
  "timestamp": "2025-05-11T10:30:45",
  "user_id": "12345678",
  "plant_type": "Corn (maize)",
  "condition": "healthy",
  "display_name": "Corn (maize) - healthy",
  "advice": "Your plant appears healthy! Continue with regular care and monitoring.",
  "image_path": "2025-05/8a7b6c5d-4e3f-2g1h-0i9j-8k7l6m5n4o3p.jpg"
}
```

### Get Prediction History for a User

**Endpoint:** `GET /api/prediction/history?user_id={user_id}&limit={limit}&offset={offset}`

**Parameters:**
- `user_id`: ID of the user whose history to retrieve (required)
- `limit`: Maximum number of results to return (default: 20)
- `offset`: Number of results to skip for pagination (default: 0)

**Example Request:**
```bash
curl "http://localhost:5000/api/prediction/history?user_id=12345678&limit=5"
```

**Example Response:**
```json
{
  "user_id": "12345678",
  "predictions": [
    {
      "prediction_id": "8a7b6c5d-4e3f-2g1h-0i9j-8k7l6m5n4o3p",
      "class_name": "Corn_(maize)___healthy",
      "confidence": 0.92,
      "timestamp": "2025-05-11T10:30:45",
      "plant_type": "Corn (maize)",
      "condition": "healthy",
      "image_path": "2025-05/8a7b6c5d-4e3f-2g1h-0i9j-8k7l6m5n4o3p.jpg"
    },
    // more predictions...
  ],
  "count": 5,
  "limit": 5,
  "offset": 0
}
```

### Get Details for a Specific Prediction

**Endpoint:** `GET /api/prediction/history/{prediction_id}`

**Parameters:**
- `prediction_id`: ID of the prediction to retrieve
- `include_image`: Set to 'true' to include base64 encoded image data (query parameter, default: false)

**Example Request:**
```bash
curl "http://localhost:5000/api/prediction/history/8a7b6c5d-4e3f-2g1h-0i9j-8k7l6m5n4o3p?include_image=true"
```

**Example Response:**
```json
{
  "prediction_id": "8a7b6c5d-4e3f-2g1h-0i9j-8k7l6m5n4o3p",
  "class_name": "Corn_(maize)___healthy",
  "confidence": 0.92,
  "timestamp": "2025-05-11T10:30:45",
  "user_id": "12345678",
  "plant_type": "Corn (maize)",
  "condition": "healthy",
  "display_name": "Corn (maize) - healthy",
  "advice": "Your plant appears healthy! Continue with regular care and monitoring.",
  "image_path": "2025-05/8a7b6c5d-4e3f-2g1h-0i9j-8k7l6m5n4o3p.jpg",
  "image_data": "base64_encoded_image_data..."
}
```

## Database Structure

Predictions are stored in the `prediction_history` collection in MongoDB with the following structure:

```javascript
{
  "prediction_id": "string", // Unique identifier for this prediction
  "user_id": "string",       // User ID or 'anonymous'
  "class_name": "string",    // Predicted class name
  "confidence": number,      // Confidence score (0-1)
  "timestamp": "string",     // ISO format timestamp
  "plant_type": "string",    // Type of plant
  "condition": "string",     // Condition (disease or healthy)
  "advice": "string",        // Treatment advice
  "image_path": "string",    // Path to saved image (optional)
  "created_at": ISODate      // When this record was created
}
```

## Image Storage

Images are stored in the `uploads` directory, organized by year-month:

```
uploads/
  2025-05/
    8a7b6c5d-4e3f-2g1h-0i9j-8k7l6m5n4o3p.jpg
    ...
```

The image path is stored in the prediction record as a relative path from the uploads directory.

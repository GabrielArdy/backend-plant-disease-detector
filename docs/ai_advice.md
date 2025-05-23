# AI-Powered Plant Disease Advice

This document explains how to use the new Gemini AI powered plant disease advice feature.

## Overview

The backend now integrates with Google's Gemini API to provide detailed, AI-generated advice for plant diseases. This advice includes specific treatment recommendations, prevention strategies, and additional information about the disease.

## How It Works

1. When a plant disease is detected through the plant disease classifier, the system automatically generates AI-powered advice about the condition.

2. The advice is structured into three main sections:
   - **Treatment**: Specific methods to treat the current infection
   - **Prevention**: Strategies to prevent future occurrences 
   - **Additional Information**: Background on the disease including cause, progression, and impact

## Using the API

### Automatic Advice with Predictions

When you make a prediction using the `/api/prediction/predict` endpoint, the response automatically includes AI-generated advice in the `advice` field.

### Dedicated Advice Endpoint

You can also request advice directly for a specific plant and condition:

**Endpoint**: `POST /api/prediction/advice`

**Headers**:
```
Authorization: Bearer <your_jwt_token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "plant_type": "Tomato",
  "condition": "Early blight"
}
```

**Response**:
```json
{
  "plant_type": "Tomato",
  "condition": "Early blight",
  "advice": {
    "treatment": "Remove infected leaves immediately...",
    "prevention": "Practice crop rotation...",
    "additional_info": "Early blight is caused by the fungus Alternaria solani...",
    "error": null
  }
}
```

## Fallback Mechanism (Enhanced May 15, 2025)

If the Gemini API is unavailable or encounters an error, the system will fall back to a built-in advice database that provides basic guidance for common plant diseases. The fallback system has been enhanced with the following improvements:

1. **Robust Response Parsing**: Improved algorithms for parsing AI-generated responses with multiple pattern recognition approaches
   
2. **Multi-stage Fallbacks**:
   - First tries to extract advice using strict section header patterns
   - If that fails, uses a more flexible pattern matching approach
   - Finally falls back to pre-defined advice templates for common conditions
   
3. **Comprehensive Templates**: Complete advice templates for common conditions like Tomato Early Blight that include:
   - Detailed treatment instructions with organic and conventional options
   - Comprehensive prevention strategies covering cultural practices and environmental management
   - Scientific background on disease causes, symptoms, and environmental factors
   
4. **Fixed Known Issues**: Resolved specific issues with advice generation for Tomato Early Blight and similar conditions that previously returned incomplete or placeholder text.

## Environment Configuration

The Gemini AI integration requires the following environment variables:

```
GENAI_API_KEY=your_api_key
GENAI_PROJECT_ID=your_project_id
GENAI_LOCATION=global
GENAI_MODEL_NAME=gemini-1.0-pro
```

These variables are defined in your `.env` file.

## Benefits Over Static Advice

Compared to the previous static advice system, the AI-powered advice offers:

1. More detailed and comprehensive treatment recommendations
2. Up-to-date information that adapts to new research and best practices
3. Customized advice that considers the specific plant type and condition
4. Natural language explanations that are easy to understand and implement

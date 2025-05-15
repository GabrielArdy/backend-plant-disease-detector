# GPU Detection for TensorFlow

This document explains how the plant disease detection API handles GPU detection and utilization for TensorFlow operations.

## Overview

The application automatically detects if a GPU is available and configures TensorFlow accordingly:

1. On startup, the system checks for available GPUs
2. If one or more GPUs are found, TensorFlow is configured to use them
3. If no GPU is available, the system falls back to CPU processing
4. Memory growth is enabled on GPUs to avoid allocating all GPU memory at once

## Implementation Details

The GPU detection functionality is implemented in `app/utils/gpu_utils.py` which provides:

1. `setup_gpu()` - Configures TensorFlow to use GPU if available, returns True if GPU is being used
2. `get_device_info()` - Returns information about available devices

These functions are called at different stages:

- During application startup to configure TensorFlow
- When loading the machine learning model to determine device placement
- When making predictions to utilize the appropriate device

## API Endpoint

The system provides an endpoint to check the hardware configuration:

```
GET /api/prediction/system-info
```

This returns details about the available computing devices:

```json
{
  "status": "success",
  "device_info": {
    "devices": [
      {
        "name": "/physical_device:GPU:0",
        "type": "GPU",
        "details": "PhysicalDevice(name='/physical_device:GPU:0', device_type='GPU')"
      },
      {
        "name": "/physical_device:CPU:0",
        "type": "CPU",
        "details": "PhysicalDevice(name='/physical_device:CPU:0', device_type='CPU')"
      }
    ],
    "using_gpu": true,
    "num_gpus": 1,
    "tensorflow_version": "2.10.0"
  }
}
```

If no GPU is available, the response will indicate CPU usage:

```json
{
  "status": "success",
  "device_info": {
    "devices": [
      {
        "name": "/physical_device:CPU:0",
        "type": "CPU",
        "details": "PhysicalDevice(name='/physical_device:CPU:0', device_type='CPU')"
      }
    ],
    "using_gpu": false,
    "num_gpus": 0,
    "tensorflow_version": "2.10.0"
  }
}
```

## Health Check

The application's health check endpoint (`/api/health`) also includes GPU information:

```json
{
  "status": "ok",
  "message": "Plant Disease API is running",
  "version": "1.0.0",
  "environment": "development",
  "hardware": {
    "using_gpu": false,
    "gpu_count": 0,
    "tensorflow_version": "2.10.0"
  }
}
```

## GPU vs. CPU Performance

Using a GPU can significantly accelerate plant disease detection:

- **CPU**: Typically 100-500ms per prediction
- **GPU**: Typically 10-50ms per prediction (10x faster)

This speed improvement is particularly noticeable when processing multiple images or when using the API in high-traffic scenarios.

## Troubleshooting

If the API is not detecting your GPU:

1. Ensure CUDA and cuDNN are properly installed
2. Check that TensorFlow was compiled with GPU support
3. Verify that your GPU is compatible with TensorFlow
4. Check the logs for any error messages during startup

For more information, see the [TensorFlow GPU guide](https://www.tensorflow.org/install/gpu).

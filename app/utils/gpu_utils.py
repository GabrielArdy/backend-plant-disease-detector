"""
Utility functions to handle GPU detection and configuration for TensorFlow.
"""
import os
import tensorflow as tf
from app.utils.log import get_logger

logger = get_logger(__name__)

def setup_gpu():
    """
    Check if GPU is available and configure TensorFlow accordingly.
    
    If a GPU is available, set up TensorFlow to use it with memory growth enabled.
    If no GPU is available, fall back to CPU and log the status.
    
    Returns:
        bool: True if GPU is being used, False if using CPU
    """
    try:
        # Check if any GPUs are available
        gpus = tf.config.experimental.list_physical_devices('GPU')
        
        if gpus:
            logger.info(f"Found {len(gpus)} GPU(s): {[gpu.name for gpu in gpus]}")
            
            # Configure TensorFlow to use memory growth to avoid allocating all GPU memory at once
            for gpu in gpus:
                try:
                    tf.config.experimental.set_memory_growth(gpu, True)
                    logger.info(f"Memory growth enabled for GPU {gpu.name}")
                except RuntimeError as e:
                    logger.warning(f"Failed to set memory growth for GPU {gpu.name}: {str(e)}")
                    
            # Log GPU info
            gpu_devices = tf.config.list_physical_devices('GPU')
            if gpu_devices:
                details = []
                for gpu in gpu_devices:
                    details.append(f"{gpu.name} ({gpu.device_type})")
                logger.info(f"Using GPU(s): {', '.join(details)}")
                
            # Set environment variable to use only necessary GPU memory
            os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'
            return True
        else:
            logger.info("No GPU found. Using CPU for TensorFlow operations.")
            
            # Make sure TensorFlow knows to use CPU
            os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
            return False
    except Exception as e:
        logger.warning(f"Error checking GPU availability: {str(e)}")
        logger.info("Defaulting to CPU for TensorFlow operations.")
        
        # Make sure TensorFlow knows to use CPU
        os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
        return False

def get_device_info():
    """
    Get information about the devices TensorFlow is using.
    
    Returns:
        dict: Information about devices being used
    """
    devices = []
    try:
        gpu_devices = tf.config.list_physical_devices('GPU')
        for device in gpu_devices:
            devices.append({
                'name': device.name,
                'type': 'GPU',
                'details': str(device)
            })
        
        cpu_devices = tf.config.list_physical_devices('CPU')
        for device in cpu_devices:
            devices.append({
                'name': device.name,
                'type': 'CPU',
                'details': str(device)
            })
            
        if not devices:
            devices.append({
                'name': 'CPU (Default)',
                'type': 'CPU',
                'details': 'Using CPU as no devices were explicitly detected'
            })
            
        return {
            'devices': devices,
            'using_gpu': len(gpu_devices) > 0,
            'num_gpus': len(gpu_devices)
        }
    except Exception as e:
        logger.error(f"Error getting device information: {str(e)}")
        return {
            'devices': [{'name': 'CPU (Default)', 'type': 'CPU', 'details': 'Error detecting devices'}],
            'using_gpu': False,
            'num_gpus': 0,
            'error': str(e)
        }

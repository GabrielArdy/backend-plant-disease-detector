import sys
import os

# Add the parent directory to the sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.gpu_utils import setup_gpu, get_device_info

if __name__ == "__main__":
    # Test GPU detection
    print("Testing GPU detection...")
    using_gpu = setup_gpu()
    print(f"Using GPU: {using_gpu}")
    
    # Get device info
    device_info = get_device_info()
    print("\nDevice Information:")
    print(f"- Using GPU: {device_info['using_gpu']}")
    print(f"- Number of GPUs: {device_info['num_gpus']}")
    print(f"- Devices:")
    for device in device_info['devices']:
        print(f"  - {device['name']} ({device['type']})")

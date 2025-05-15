#!/usr/bin/env python
import os
import numpy as np
from PIL import Image

# Create a simple brown/yellow-ish image that could pass as a diseased tomato leaf
width, height = 224, 224  # Standard model input size

# Create an image with a brownish background
image_array = np.zeros((height, width, 3), dtype=np.uint8)
image_array[:, :] = [139, 69, 19]  # Brownish color

# Add some yellowish spots (early blight characteristics)
for i in range(20):
    x = np.random.randint(10, width-10)
    y = np.random.randint(10, height-10)
    spot_size = np.random.randint(5, 20)
    
    # Draw a circular spot
    for dx in range(-spot_size, spot_size+1):
        for dy in range(-spot_size, spot_size+1):
            if dx*dx + dy*dy <= spot_size*spot_size:
                nx, ny = x+dx, y+dy
                if 0 <= nx < width and 0 <= ny < height:
                    image_array[ny, nx] = [218, 165, 32]  # Gold/yellow color

# Create a green edge to simulate the healthy part of the leaf
edge_width = 20
image_array[0:edge_width, :] = [34, 139, 34]  # Forest green
image_array[height-edge_width:height, :] = [34, 139, 34]
image_array[:, 0:edge_width] = [34, 139, 34]
image_array[:, width-edge_width:width] = [34, 139, 34]

# Convert to PIL Image
image = Image.fromarray(image_array)

# Ensure directory exists
os.makedirs('test_data', exist_ok=True)

# Save the image
image_path = os.path.join('test_data', 'tomato_early_blight.jpg')
image.save(image_path)

print(f"Created test image at: {image_path}")

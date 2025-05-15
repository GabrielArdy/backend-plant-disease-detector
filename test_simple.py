"""
Verify basic Python functionality
"""

print("Python is working!")

# Test dictionary functionality
test_dict = {
    'tomato': {
        'blight': "Treatment for blight",
        'general': "General treatment"
    }
}

# Access nested dictionary
plant = 'tomato'
condition = 'blight'
if plant in test_dict:
    plant_dict = test_dict[plant]
    if condition in plant_dict:
        print(f"Found specific advice: {plant_dict[condition]}")
    else:
        print(f"Using general advice: {plant_dict['general']}")
else:
    print("Using default advice")

print("Test completed successfully!")

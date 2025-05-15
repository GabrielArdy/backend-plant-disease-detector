import os
import google.generativeai as genai

# Configure the API
api_key = os.getenv('GENAI_API_KEY')
if not api_key:
    print("No API key found - please set GENAI_API_KEY environment variable")
    exit(1)

genai.configure(api_key=api_key)

# List available models
for model in genai.list_models():
    if "generateContent" in model.supported_generation_methods:
        print(f"Model name: {model.name}")
        print(f"Display name: {model.display_name}")
        print(f"Supported methods: {model.supported_generation_methods}")
        print("---")

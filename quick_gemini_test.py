import os
import google.generativeai as genai

# Print API key availability
api_key = os.getenv('GENAI_API_KEY')
print(f"API key available: {bool(api_key)}")
if not api_key:
    print("No API key found - please set GENAI_API_KEY environment variable")
    exit(1)

# Configure the API
genai.configure(api_key=api_key)

# Create a model 
model = genai.GenerativeModel('gemini-pro')

# Generate a response
response = model.generate_content("What is the capital of France?")

print("Response text:", response.text)

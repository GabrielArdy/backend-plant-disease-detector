import os
from dotenv import load_dotenv
from pathlib import Path

# Find and load the local.env file
env_path = Path(__file__).parent / 'local.env'
if env_path.exists():
    print(f"Loading environment variables from {env_path}")
    load_dotenv(dotenv_path=env_path)
else:
    print(f"Warning: Environment file {env_path} not found. Using default variables.")
    # Try to load from .env as fallback
    load_dotenv()

print("\nChecking environment variables...")
print("\n== Gemini API Configuration ==")
print(f"GENAI_API_KEY: {'Set' if os.getenv('GENAI_API_KEY') else 'Not set'}")
print(f"GENAI_MODEL_NAME: {os.getenv('GENAI_MODEL_NAME', 'Not set (will use default)')}")
print(f"GENAI_PROJECT_ID: {os.getenv('GENAI_PROJECT_ID', 'Not set')}")
print(f"GENAI_LOCATION: {os.getenv('GENAI_LOCATION', 'Not set (will use default)')}")

print("\n== Flask Configuration ==")
print(f"FLASK_ENV: {os.getenv('FLASK_ENV', 'Not set')}")
print(f"MONGO_URI: {os.getenv('MONGO_URI', 'Not set')}")
print(f"SECRET_KEY: {'Set' if os.getenv('SECRET_KEY') else 'Not set'}")
print(f"JWT_SECRET_KEY: {'Set' if os.getenv('JWT_SECRET_KEY') else 'Not set'}")

# Show the actual values (with masking for sensitive data)
print("\n== Actual Values (Truncated for Security) ==")
api_key = os.getenv('GENAI_API_KEY', '')
print(f"GENAI_API_KEY: {api_key[:4] + '****' if api_key else 'Not set'}")
print(f"GENAI_MODEL_NAME: {os.getenv('GENAI_MODEL_NAME', 'Not set')}")

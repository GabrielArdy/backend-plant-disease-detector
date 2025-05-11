import requests
import json
from pprint import pprint

# Base URL for the API
BASE_URL = "http://localhost:5000/api/auth"

def test_register():
    """
    Test register endpoint
    """
    url = f"{BASE_URL}/register"
    data = {
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "username": "testuser",
        "password": "password123"
    }
    
    print("\nTesting user registration...")
    try:
        response = requests.post(url, json=data)
        print(f"Status code: {response.status_code}")
        print("Response:")
        pprint(response.json())
        return response.json().get('user_id')
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def test_login(username="testuser", password="password123"):
    """
    Test login endpoint
    """
    url = f"{BASE_URL}/login"
    data = {
        "username": username,
        "password": password
    }
    
    print("\nTesting user login...")
    try:
        response = requests.post(url, json=data)
        print(f"Status code: {response.status_code}")
        print("Response:")
        pprint(response.json())
        
        if response.status_code == 200:
            return response.json().get('data', {}).get('token')
        return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def test_get_profile(token):
    """
    Test get profile endpoint
    """
    url = f"{BASE_URL}/profile"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    print("\nTesting get profile...")
    try:
        response = requests.get(url, headers=headers)
        print(f"Status code: {response.status_code}")
        print("Response:")
        pprint(response.json())
    except Exception as e:
        print(f"Error: {str(e)}")

def test_update_profile(token):
    """
    Test update profile endpoint
    """
    url = f"{BASE_URL}/profile"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    data = {
        "avatar": "https://example.com/avatar.jpg",
        "cover_image": "https://example.com/cover.jpg",
        "description": "This is a test profile"
    }
    
    print("\nTesting update profile...")
    try:
        response = requests.put(url, headers=headers, json=data)
        print(f"Status code: {response.status_code}")
        print("Response:")
        pprint(response.json())
    except Exception as e:
        print(f"Error: {str(e)}")

def run_all_tests():
    """
    Run all tests in sequence
    """
    # Register user
    user_id = test_register()
    
    # Login
    token = test_login()
    
    if token:
        # Get profile
        test_get_profile(token)
        
        # Update profile
        test_update_profile(token)
        
        # Get profile again to see changes
        test_get_profile(token)

if __name__ == "__main__":
    run_all_tests()

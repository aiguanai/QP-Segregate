"""Test the /me endpoint directly"""
import requests
import json

# First, get a token
print("Step 1: Getting login token...")
login_response = requests.post(
    'http://127.0.0.1:8000/api/auth/login',
    data={'username': 'admin', 'password': 'admin123'},
    headers={'Content-Type': 'application/x-www-form-urlencoded'},
    timeout=10
)

if login_response.status_code == 200:
    token = login_response.json()['access_token']
    print(f"✅ Got token: {token[:50]}...")
    
    print("\nStep 2: Testing /me endpoint...")
    me_response = requests.get(
        'http://127.0.0.1:8000/api/auth/me',
        headers={'Authorization': f'Bearer {token}'},
        timeout=60
    )
    
    print(f"Status Code: {me_response.status_code}")
    print(f"Response: {me_response.text}")
    
    if me_response.status_code == 200:
        print("✅ /me endpoint works!")
        print(json.dumps(me_response.json(), indent=2))
    else:
        print(f"❌ /me endpoint failed: {me_response.text}")
else:
    print(f"❌ Login failed: {login_response.text}")


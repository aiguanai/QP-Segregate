"""Test login directly to see what's happening"""
import requests
import json

# Test the login endpoint
print("Testing login endpoint...")
print("=" * 60)

try:
    response = requests.post(
        'http://127.0.0.1:8000/api/auth/login',
        data={
            'username': 'admin',
            'password': 'admin123'
        },
        headers={
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        timeout=5
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Login successful!")
        print(f"   Token: {data.get('access_token', '')[:50]}...")
    else:
        print(f"❌ Login failed: {response.text}")
        
except requests.exceptions.Timeout:
    print("❌ Request timed out - server is hanging!")
except Exception as e:
    print(f"❌ Error: {e}")

print("=" * 60)


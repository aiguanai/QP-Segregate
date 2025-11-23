"""
Test the login API endpoint directly
"""
import requests
import sys

def test_login_api():
    """Test the login API endpoint"""
    print("🔍 Testing Login API Endpoint...")
    
    # Test data
    url = "http://localhost:8000/api/auth/login"
    data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        print(f"📡 Sending POST request to: {url}")
        print(f"   Username: {data['username']}")
        print(f"   Password: {data['password']}")
        
        response = requests.post(
            url,
            data=data,  # Form data for OAuth2
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        print(f"\n📊 Response Status: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Login SUCCESSFUL!")
            print(f"   Access Token: {result.get('access_token', 'N/A')[:50]}...")
            print(f"   Token Type: {result.get('token_type', 'N/A')}")
            return True
        else:
            print(f"❌ Login FAILED!")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Backend server is not running!")
        print("   Please start the backend server with: uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_login_api()
    sys.exit(0 if success else 1)



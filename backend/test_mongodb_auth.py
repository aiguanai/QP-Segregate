"""
Test MongoDB authentication with different connection string formats
"""
import urllib.parse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_mongodb_connection(connection_string, description):
    """Test a MongoDB connection string"""
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"{'='*60}")
    print(f"Connection string: {connection_string[:80]}...")
    
    try:
        from pymongo import MongoClient
        
        client = MongoClient(connection_string, serverSelectionTimeoutMS=10000)
        # Test connection
        client.server_info()
        print("✅ Connection successful!")
        client.close()
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def main():
    print("="*60)
    print("MongoDB Authentication Troubleshooter")
    print("="*60)
    
    try:
        from app.core.config import settings
        
        original_url = settings.MONGODB_URL
        print(f"\n📋 Current MONGODB_URL from .env:")
        print(f"   {original_url}")
        
        # Parse the connection string
        if not original_url.startswith('mongodb+srv://'):
            print("\n❌ ERROR: Connection string must start with 'mongodb+srv://'")
            return
        
        # Extract parts
        auth_part = original_url.replace('mongodb+srv://', '').split('@')[0]
        if ':' not in auth_part:
            print("\n❌ ERROR: Username:password format not found")
            return
        
        username, password = auth_part.split(':', 1)
        rest = '@' + original_url.split('@')[1]
        
        print(f"\n📊 Parsed Components:")
        print(f"   Username: {username}")
        print(f"   Password: {'*' * len(password)} (length: {len(password)})")
        
        # Test 1: Original connection string
        test_mongodb_connection(original_url, "Original Connection String")
        
        # Test 2: URL-encoded password
        encoded_password = urllib.parse.quote(password, safe='')
        if encoded_password != password:
            encoded_url = f"mongodb+srv://{username}:{encoded_password}{rest}"
            test_mongodb_connection(encoded_url, "With URL-Encoded Password")
        
        # Test 3: Check for common issues
        print(f"\n{'='*60}")
        print("Common Issues Checklist:")
        print(f"{'='*60}")
        
        print("\n1. ✅ Connection string format: Correct (mongodb+srv://)")
        print("2. ⚠️  Verify in MongoDB Atlas:")
        print("   → Go to https://cloud.mongodb.com")
        print("   → Database Access")
        print("   → Check username matches: " + username)
        print("   → Verify password is correct")
        print("   → User should have 'Read and write to any database' privileges")
        
        print("\n3. ⚠️  Network Access:")
        print("   → Network Access → Add IP Address")
        print("   → For development: Allow 0.0.0.0/0 (all IPs)")
        print("   → For production: Add your server IP only")
        
        print("\n4. ⚠️  Database Name:")
        if '/qpaper_ai' in original_url:
            print("   ✅ Database name found in connection string")
        else:
            print("   ❌ Database name missing! Should include /qpaper_ai")
            print("   → Add /qpaper_ai before the ? in connection string")
        
        print("\n5. 🔧 Try resetting password:")
        print("   → MongoDB Atlas → Database Access")
        print("   → Click 'Edit' on your user")
        print("   → Click 'Edit Password'")
        print("   → Set a new simple password (no special chars)")
        print("   → Update .env file with new password")
        
    except ImportError as e:
        print(f"\n❌ Error: {e}")
        print("   Make sure venv is activated and dependencies are installed")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()


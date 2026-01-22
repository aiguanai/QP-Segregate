"""
Diagnose and fix MongoDB connection issues
"""
import urllib.parse
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def diagnose_mongodb():
    """Diagnose MongoDB connection issues"""
    print("=" * 60)
    print("MongoDB Connection Diagnostics")
    print("=" * 60)
    
    try:
        from app.core.config import settings
        
        if not settings.MONGODB_URL:
            print("\n❌ MONGODB_URL not set in .env file")
            return
        
        connection_string = settings.MONGODB_URL
        print(f"\n📋 Current MONGODB_URL from .env:")
        print(f"   {connection_string[:80]}..." if len(connection_string) > 80 else f"   {connection_string}")
        
        # Parse connection string
        if not connection_string.startswith('mongodb+srv://'):
            print("\n❌ ERROR: Connection string must start with 'mongodb+srv://' for MongoDB Atlas")
            print("   Current format is incorrect")
            return
        
        # Extract username and password
        try:
            # Remove mongodb+srv://
            auth_part = connection_string.replace('mongodb+srv://', '').split('@')[0]
            
            if ':' not in auth_part:
                print("\n❌ ERROR: Username:password format not found")
                return
            
            username, password = auth_part.split(':', 1)
            
            print(f"\n📊 Connection String Analysis:")
            print(f"   Username: {username}")
            print(f"   Password length: {len(password)}")
            
            # Check for placeholder
            if '<password>' in connection_string.lower() or '<PASSWORD>' in connection_string:
                print("\n❌ ERROR: Connection string contains placeholder '<password>'")
                print("   You need to replace it with your actual password")
                return
            
            # Check for special characters
            special_chars = ['@', '#', '$', '%', '&', '+', '=', '?', '/', ':', ';', '!', '*', '(', ')', '[', ']']
            found_special = [c for c in special_chars if c in password]
            
            if found_special:
                print(f"\n⚠️  WARNING: Password contains special characters: {found_special}")
                print("   These characters need to be URL-encoded in the connection string")
                
                # URL encode the password
                encoded_password = urllib.parse.quote(password, safe='')
                
                if encoded_password != password:
                    print(f"\n✅ SOLUTION: Use URL-encoded password")
                    # Reconstruct connection string with encoded password
                    parts = connection_string.split('@')
                    if len(parts) == 2:
                        auth_part_encoded = f"{username}:{encoded_password}"
                        fixed_url = f"mongodb+srv://{auth_part_encoded}@{parts[1]}"
                        
                        print(f"\n📝 Fixed Connection String:")
                        print(f"   {fixed_url}")
                        print(f"\n💡 Copy this to your .env file as MONGODB_URL")
                else:
                    print(f"\n✅ Password encoding check passed")
            else:
                print(f"\n✅ No special characters found in password")
            
            # Check database name
            if '/qpaper_ai' not in connection_string and '/?' not in connection_string:
                print(f"\n⚠️  WARNING: Database name might be missing")
                print("   Connection string should include: /qpaper_ai")
            
            # Check query parameters
            if 'retryWrites=true' not in connection_string:
                print(f"\n⚠️  WARNING: Recommended query parameters missing")
                print("   Should include: ?retryWrites=true&w=majority")
            
        except Exception as e:
            print(f"\n❌ Error parsing connection string: {e}")
            return
        
        print("\n" + "=" * 60)
        print("🔍 Troubleshooting Steps:")
        print("=" * 60)
        print("\n1. Verify MongoDB Atlas Settings:")
        print("   → Go to https://cloud.mongodb.com")
        print("   → Database Access → Check your username")
        print("   → Network Access → Ensure your IP is whitelisted (0.0.0.0/0 for dev)")
        
        print("\n2. Reset Password (if needed):")
        print("   → Database Access → Click 'Edit' on your user")
        print("   → Click 'Edit Password' → Set new password")
        print("   → Copy the new password")
        
        print("\n3. Get Fresh Connection String:")
        print("   → Click 'Connect' on your cluster")
        print("   → Choose 'Connect your application'")
        print("   → Copy the connection string")
        print("   → Replace <password> with your actual password")
        print("   → Add /qpaper_ai before the ?")
        
        print("\n4. If password has special characters:")
        print("   → Use the fixed connection string shown above")
        print("   → Or manually URL-encode special characters")
        
    except ImportError as e:
        print(f"\n❌ Error importing settings: {e}")
        print("   Make sure you're in the backend directory and venv is activated")

if __name__ == "__main__":
    diagnose_mongodb()


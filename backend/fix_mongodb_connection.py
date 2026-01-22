"""
Helper script to fix MongoDB connection string issues
"""
import urllib.parse
import sys

def url_encode_password(password):
    """URL encode special characters in password"""
    return urllib.parse.quote(password, safe='')

def fix_mongodb_url(connection_string):
    """
    Fix common MongoDB connection string issues
    """
    print("=" * 60)
    print("MongoDB Connection String Fixer")
    print("=" * 60)
    
    # Check if it's a mongodb+srv:// connection
    if not connection_string.startswith('mongodb+srv://'):
        print("⚠️  Warning: Connection string should start with 'mongodb+srv://' for Atlas")
        print("   Current format:", connection_string[:50] + "...")
        return None
    
    # Parse the connection string
    try:
        # Extract parts
        if '<password>' in connection_string or '<PASSWORD>' in connection_string:
            print("\n❌ Error: Connection string contains placeholder '<password>'")
            print("   You need to replace it with your actual password")
            return None
        
        # Check for password in the URL
        parts = connection_string.split('@')
        if len(parts) != 2:
            print("\n❌ Error: Invalid connection string format")
            return None
        
        auth_part = parts[0].replace('mongodb+srv://', '')
        if ':' not in auth_part:
            print("\n❌ Error: Username:password not found in connection string")
            return None
        
        username, password = auth_part.split(':', 1)
        
        print(f"\n📋 Current Connection String Analysis:")
        print(f"   Username: {username}")
        print(f"   Password: {'*' * len(password)} (length: {len(password)})")
        
        # Check for special characters that need encoding
        special_chars = ['@', '#', '$', '%', '&', '+', '=', '?', '/', ':', ';']
        has_special = any(char in password for char in special_chars)
        
        if has_special:
            print(f"\n⚠️  Warning: Password contains special characters that may need URL encoding")
            print(f"   Special characters found: {[c for c in special_chars if c in password]}")
            
            # URL encode the password
            encoded_password = url_encode_password(password)
            if encoded_password != password:
                print(f"\n✅ Fixed Connection String (with URL-encoded password):")
                fixed_url = connection_string.replace(f":{password}@", f":{encoded_password}@")
                print(f"   {fixed_url}")
                return fixed_url
            else:
                print(f"\n✅ Password doesn't need encoding")
        else:
            print(f"\n✅ No special characters found - password should work as-is")
        
        return connection_string
        
    except Exception as e:
        print(f"\n❌ Error parsing connection string: {e}")
        return None

def main():
    print("\n" + "=" * 60)
    print("MongoDB Connection Troubleshooting Guide")
    print("=" * 60)
    
    print("\n📝 Common Issues and Solutions:")
    print("\n1. ❌ Wrong Password")
    print("   → Go to MongoDB Atlas → Database Access")
    print("   → Find your user → Click 'Edit' → Reset password")
    print("   → Copy the new password")
    
    print("\n2. ❌ Special Characters in Password")
    print("   → Passwords with @, #, $, %, &, +, =, ?, / need URL encoding")
    print("   → Use this script to auto-encode your password")
    
    print("\n3. ❌ Wrong Username")
    print("   → Verify username in MongoDB Atlas → Database Access")
    print("   → Username is case-sensitive")
    
    print("\n4. ❌ IP Not Whitelisted")
    print("   → Go to MongoDB Atlas → Network Access")
    print("   → Add your IP address (or 0.0.0.0/0 for development)")
    
    print("\n5. ❌ Database Name Missing")
    print("   → Connection string should end with: /qpaper_ai?retryWrites=true&w=majority")
    
    print("\n" + "=" * 60)
    print("\n🔧 To fix your connection string:")
    print("\n1. Get your connection string from MongoDB Atlas:")
    print("   → Click 'Connect' on your cluster")
    print("   → Choose 'Connect your application'")
    print("   → Copy the connection string")
    
    print("\n2. It should look like:")
    print("   mongodb+srv://username:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority")
    
    print("\n3. Replace <password> with your actual password")
    
    print("\n4. Add database name before the ?:")
    print("   mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/qpaper_ai?retryWrites=true&w=majority")
    
    print("\n5. If password has special characters, run this script with your connection string:")
    print("   python fix_mongodb_connection.py 'your-connection-string'")
    
    # If connection string provided as argument, fix it
    if len(sys.argv) > 1:
        connection_string = sys.argv[1]
        print("\n" + "=" * 60)
        fixed = fix_mongodb_url(connection_string)
        if fixed:
            print("\n" + "=" * 60)
            print("✅ Copy this fixed connection string to your .env file:")
            print("=" * 60)
            print(f"\nMONGODB_URL={fixed}\n")

if __name__ == "__main__":
    main()


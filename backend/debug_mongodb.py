"""
Detailed MongoDB connection debugging
"""
import sys
import os
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def debug_mongodb():
    """Debug MongoDB connection in detail"""
    print("="*70)
    print("MongoDB Connection Debugger")
    print("="*70)
    
    try:
        from app.core.config import settings
        
        url = settings.MONGODB_URL
        print(f"\n📋 Current MONGODB_URL:")
        print(f"   {url}")
        
        # Parse connection string manually
        if not url.startswith('mongodb+srv://'):
            print("\n❌ ERROR: Must start with 'mongodb+srv://'")
            return
        
        # Extract components
        try:
            # Remove protocol
            without_protocol = url.replace('mongodb+srv://', '')
            
            # Split at @
            if '@' not in without_protocol:
                print("\n❌ ERROR: No @ found in connection string")
                return
            
            auth_part, server_part = without_protocol.split('@', 1)
            
            # Split username and password
            if ':' not in auth_part:
                print("\n❌ ERROR: No : found between username and password")
                return
            
            username, password = auth_part.split(':', 1)
            
            print(f"\n📊 Parsed Components:")
            print(f"   Username: '{username}'")
            print(f"   Password: '{'*' * len(password)}' (length: {len(password)})")
            print(f"   Server: {server_part[:60]}...")
            
            # Check for database name
            if '/qpaper_ai' in server_part:
                print(f"   ✅ Database name found: /qpaper_ai")
            else:
                print(f"   ❌ Database name missing!")
                print(f"   → Should include /qpaper_ai before the ?")
            
            # Test different connection string variations
            print(f"\n{'='*70}")
            print("Testing Connection String Variations")
            print(f"{'='*70}")
            
            from pymongo import MongoClient
            from pymongo.errors import OperationFailure, ServerSelectionTimeoutError
            
            # Test 1: Original
            print(f"\n1️⃣  Testing original connection string...")
            try:
                client = MongoClient(url, serverSelectionTimeoutMS=10000)
                client.server_info()
                print("   ✅ SUCCESS with original string!")
                client.close()
                return
            except OperationFailure as e:
                print(f"   ❌ Authentication failed: {e}")
            except Exception as e:
                print(f"   ❌ Error: {e}")
            
            # Test 2: URL-encoded password
            encoded_pass = urllib.parse.quote(password, safe='')
            if encoded_pass != password:
                encoded_url = f"mongodb+srv://{username}:{encoded_pass}@{server_part}"
                print(f"\n2️⃣  Testing with URL-encoded password...")
                try:
                    client = MongoClient(encoded_url, serverSelectionTimeoutMS=10000)
                    client.server_info()
                    print("   ✅ SUCCESS with encoded password!")
                    print(f"\n💡 Use this connection string in your .env:")
                    print(f"   MONGODB_URL={encoded_url}")
                    client.close()
                    return
                except Exception as e:
                    print(f"   ❌ Failed: {e}")
            
            # Test 3: Without database name (connect to admin)
            if '/qpaper_ai' in server_part:
                server_no_db = server_part.replace('/qpaper_ai', '')
                test_url = f"mongodb+srv://{username}:{password}@{server_no_db}"
                print(f"\n3️⃣  Testing without database name (admin connection)...")
                try:
                    client = MongoClient(test_url, serverSelectionTimeoutMS=10000)
                    client.server_info()
                    print("   ✅ SUCCESS! Authentication works, but database name might be wrong")
                    print("   → Try adding /qpaper_ai to your connection string")
                    client.close()
                except Exception as e:
                    print(f"   ❌ Failed: {e}")
            
            # Test 4: Check if it's a network/IP issue
            print(f"\n4️⃣  Testing network connectivity...")
            try:
                # Try to connect with a timeout
                client = MongoClient(url, serverSelectionTimeoutMS=5000, connectTimeoutMS=5000)
                client.server_info()
                print("   ✅ Network connection successful")
                client.close()
            except ServerSelectionTimeoutError:
                print("   ❌ Network timeout - check IP whitelist in MongoDB Atlas")
                print("   → Go to Network Access → Add your IP (0.0.0.0/0 for dev)")
            except Exception as e:
                print(f"   ⚠️  Network test: {e}")
            
        except Exception as e:
            print(f"\n❌ Error parsing connection string: {e}")
            import traceback
            traceback.print_exc()
        
        # Final recommendations
        print(f"\n{'='*70}")
        print("🔧 Recommended Actions:")
        print(f"{'='*70}")
        print("\n1. Verify credentials in MongoDB Atlas:")
        print("   → https://cloud.mongodb.com → Database Access")
        print("   → Check username: " + username)
        print("   → Reset password if unsure")
        
        print("\n2. Check Network Access:")
        print("   → Network Access → Add IP Address")
        print("   → For development: 0.0.0.0/0 (Allow from anywhere)")
        
        print("\n3. Verify connection string format:")
        print("   → Should be: mongodb+srv://username:password@cluster.net/dbname?options")
        print("   → Database name (/qpaper_ai) should be before the ?")
        
        print("\n4. Try creating a new database user:")
        print("   → Database Access → Add New Database User")
        print("   → Username: qpaper_user (simple, no special chars)")
        print("   → Password: Create a simple password (no special chars)")
        print("   → Privileges: Read and write to any database")
        print("   → Use new credentials in connection string")
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("   Make sure you're in the backend directory with venv activated")
        print("   Run: pip install pymongo")

if __name__ == "__main__":
    debug_mongodb()


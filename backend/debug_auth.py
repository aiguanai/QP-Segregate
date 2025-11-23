"""
Debug authentication to see what's happening
"""
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from passlib.context import CryptContext
from app.core.config import settings
from app.models.user import User
from app.api.auth import authenticate_user, get_user, verify_password

def debug_auth():
    """Debug the authentication process"""
    print("🔍 Debugging Authentication...")
    
    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        username = "admin"
        password = "admin123"
        
        print(f"\n1️⃣ Looking up user: {username}")
        user = get_user(db, username)
        
        if not user:
            print("   ❌ User not found!")
            return
        
        print(f"   ✅ User found:")
        print(f"      ID: {user.user_id}")
        print(f"      Username: {user.username}")
        print(f"      Email: {user.email}")
        print(f"      Role: {user.role}")
        print(f"      Is Active: {user.is_active}")
        print(f"      Password Hash: {user.password_hash[:60]}...")
        
        print(f"\n2️⃣ Verifying password: {password}")
        pwd_context = CryptContext(schemes=["bcrypt", "pbkdf2_sha256"], deprecated="auto")
        
        try:
            is_valid = pwd_context.verify(password, user.password_hash)
            print(f"   Result: {'✅ VALID' if is_valid else '❌ INVALID'}")
        except Exception as e:
            print(f"   ❌ Verification error: {e}")
            import traceback
            traceback.print_exc()
            return
        
        print(f"\n3️⃣ Testing authenticate_user function:")
        result = authenticate_user(db, username, password)
        if result:
            print(f"   ✅ Authentication SUCCESSFUL!")
            print(f"      User: {result.username}")
        else:
            print(f"   ❌ Authentication FAILED!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_auth()



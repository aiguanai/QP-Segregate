"""
Test script to verify admin login credentials
"""
import sys
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from passlib.context import CryptContext
from app.core.config import settings
from app.models.user import User

def test_admin_login():
    """Test admin login credentials"""
    print("🔍 Testing Admin Login...")
    
    # Create database connection
    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Find admin user
        admin = session.query(User).filter(User.username == "admin").first()
        
        if not admin:
            print("❌ Admin user not found in database!")
            print("   Run: python create_admin.py")
            return False
        
        print(f"✅ Admin user found:")
        print(f"   Username: {admin.username}")
        print(f"   Email: {admin.email}")
        print(f"   Role: {admin.role}")
        print(f"   Is Active: {admin.is_active}")
        print(f"   Password Hash: {admin.password_hash[:50]}...")
        
        # Test password verification
        pwd_context = CryptContext(schemes=["bcrypt", "pbkdf2_sha256"], deprecated="auto")
        
        test_password = "admin123"
        print(f"\n🔐 Testing password verification...")
        print(f"   Testing password: {test_password}")
        
        try:
            is_valid = pwd_context.verify(test_password, admin.password_hash)
            if is_valid:
                print("   ✅ Password verification SUCCESSFUL!")
                return True
            else:
                print("   ❌ Password verification FAILED!")
                print("   The password hash doesn't match 'admin123'")
                print("\n   💡 Solution: Run 'python create_admin.py' to reset the password")
                return False
        except Exception as e:
            print(f"   ❌ Error verifying password: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        session.close()

if __name__ == "__main__":
    success = test_admin_login()
    sys.exit(0 if success else 1)


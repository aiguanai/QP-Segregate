"""
Complete fix for login issues - ensures admin user exists with correct password
"""
import sys
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from passlib.context import CryptContext
from app.core.config import settings
from app.models.user import User

def fix_login():
    """Fix login by ensuring admin user exists with correct password"""
    print("🔧 Fixing Login Issues...")
    
    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Use pbkdf2_sha256 for hashing (bcrypt has version issues)
        # But auth.py can verify both
        pwd_context_hash = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
        pwd_context_verify = CryptContext(schemes=["bcrypt", "pbkdf2_sha256"], deprecated="auto")
        
        # Check if admin exists
        admin = session.query(User).filter(User.username == "admin").first()
        
        # Hash password with pbkdf2_sha256
        password_hash = pwd_context_hash.hash("admin123")
        
        if admin:
            print("📝 Updating existing admin user...")
            admin.password_hash = password_hash
            admin.email = "admin@qpaper.ai"
            admin.role = "ADMIN"
            admin.is_active = True
        else:
            print("➕ Creating new admin user...")
            admin = User(
                username="admin",
                email="admin@qpaper.ai",
                password_hash=password_hash,
                role="ADMIN",
                is_active=True
            )
            session.add(admin)
        
        session.commit()
        
        # Verify it works
        print("\n✅ Verifying password...")
        is_valid = pwd_context_verify.verify("admin123", admin.password_hash)
        
        if is_valid:
            print("✅ Admin user fixed successfully!")
            print("\n📋 Login Credentials:")
            print("   Username: admin")
            print("   Password: admin123")
            print("\n⚠️  IMPORTANT: Restart your backend server for changes to take effect!")
            print("   Run: uvicorn app.main:app --reload")
            return True
        else:
            print("❌ Password verification failed after update!")
            return False
            
    except Exception as e:
        session.rollback()
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        session.close()

if __name__ == "__main__":
    success = fix_login()
    sys.exit(0 if success else 1)


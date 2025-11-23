"""
Script to create or reset admin user
Run this if you're having login issues: python create_admin.py
"""
import os
import sys
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from passlib.context import CryptContext
from app.core.config import settings
from app.models.user import User

def create_or_reset_admin():
    """Create or reset admin user"""
    print("🔐 Creating/Resetting Admin User...")
    
    # Create database connection
    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Check if admin exists
        admin = session.query(User).filter(User.username == "admin").first()
        
        # Create password hasher
        try:
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            password_hash = pwd_context.hash("admin123")
        except Exception as e:
            print(f"⚠️  Bcrypt failed ({e}), using pbkdf2_sha256 instead")
            pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
            password_hash = pwd_context.hash("admin123")
        
        if admin:
            # Update existing admin
            print("📝 Admin user exists. Updating password...")
            admin.password_hash = password_hash
            admin.email = "admin@qpaper.ai"
            admin.role = "ADMIN"
            admin.is_active = True
            session.commit()
            print("✅ Admin password reset successfully!")
        else:
            # Create new admin
            print("➕ Creating new admin user...")
            admin_user = User(
                username="admin",
                email="admin@qpaper.ai",
                password_hash=password_hash,
                role="ADMIN",
                is_active=True
            )
            session.add(admin_user)
            session.commit()
            print("✅ Admin user created successfully!")
        
        print("\n📋 Admin Credentials:")
        print("   Username: admin")
        print("   Password: admin123")
        print("   Email: admin@qpaper.ai")
        print("\n✅ You can now log in with these credentials!")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        session.close()

if __name__ == "__main__":
    create_or_reset_admin()


"""Test admin login and verify user exists"""
from app.core.database import SessionLocal
from app.models.user import User
from passlib.context import CryptContext

db = SessionLocal()
user = db.query(User).filter(User.username == 'admin').first()

if user:
    print(f"✅ User found: {user.username}")
    print(f"   Role: {user.role}")
    print(f"   Is Active: {user.is_active}")
    print(f"   Email: {user.email}")
    
    # Test password verification
    pwd_context = CryptContext(schemes=['bcrypt', 'pbkdf2_sha256'], deprecated='auto')
    verified = pwd_context.verify('admin123', user.password_hash)
    print(f"   Password 'admin123' verified: {verified}")
    
    if not verified:
        print("\n⚠️  Password verification failed!")
        print("   Let's recreate the admin user with correct password hash...")
        
        # Recreate password hash
        try:
            new_hash = pwd_context.hash('admin123')
            user.password_hash = new_hash
            user.is_active = True
            db.commit()
            print("✅ Admin user password updated!")
            
            # Verify again
            verified = pwd_context.verify('admin123', user.password_hash)
            print(f"   Password verification after update: {verified}")
        except Exception as e:
            print(f"❌ Error updating password: {e}")
            db.rollback()
else:
    print("❌ Admin user not found!")
    print("   Run: python init_db.py")

db.close()

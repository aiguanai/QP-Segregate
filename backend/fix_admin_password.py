"""Fix admin password hash to ensure it works with the auth system"""
from app.core.database import SessionLocal
from app.models.user import User
from passlib.context import CryptContext

# Use the same context as auth.py
pwd_context = CryptContext(schemes=["bcrypt", "pbkdf2_sha256"], deprecated="auto")

db = SessionLocal()
user = db.query(User).filter(User.username == 'admin').first()

if user:
    print(f"Found user: {user.username}")
    print(f"Current hash: {user.password_hash[:60]}...")
    
    # Test current hash
    current_works = pwd_context.verify('admin123', user.password_hash)
    print(f"Current hash verification: {current_works}")
    
    if not current_works:
        print("\n⚠️  Current hash doesn't verify. Creating new hash...")
        # Create new hash using bcrypt (preferred)
        try:
            new_hash = pwd_context.hash('admin123')
            print(f"New hash: {new_hash[:60]}...")
            
            # Verify new hash works
            if pwd_context.verify('admin123', new_hash):
                user.password_hash = new_hash
                user.is_active = True
                db.commit()
                print("✅ Password hash updated successfully!")
                
                # Verify it works now
                final_check = pwd_context.verify('admin123', user.password_hash)
                print(f"Final verification: {final_check}")
            else:
                print("❌ New hash doesn't verify - something is wrong!")
        except Exception as e:
            print(f"❌ Error: {e}")
            db.rollback()
    else:
        print("✅ Current hash works correctly!")
        print("   The issue might be elsewhere. Check server logs.")
else:
    print("❌ Admin user not found!")
    print("   Run: python init_db.py")

db.close()


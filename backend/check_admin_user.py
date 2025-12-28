"""Quick check of admin user status"""
from app.core.database import SessionLocal
from app.models.user import User
from passlib.context import CryptContext

db = SessionLocal()
user = db.query(User).filter(User.username == "admin").first()

if user:
    print(f"✅ Admin user found")
    print(f"   Username: {user.username}")
    print(f"   Email: {user.email}")
    print(f"   Role: {user.role}")
    print(f"   Is Active: {user.is_active}")
    print(f"   Password hash: {user.password_hash[:60]}...")
    
    # Test password verification
    ctx = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
    verified = ctx.verify("admin123", user.password_hash)
    print(f"   Password 'admin123' verified: {verified}")
    
    if not verified:
        print("\n⚠️  Password doesn't verify! Recreating...")
        new_hash = ctx.hash("admin123")
        user.password_hash = new_hash
        user.is_active = True
        db.commit()
        print("✅ Password hash updated!")
        
        # Verify again
        verified2 = ctx.verify("admin123", user.password_hash)
        print(f"   New hash verification: {verified2}")
else:
    print("❌ Admin user not found!")
    print("   Run: python init_db.py")

db.close()


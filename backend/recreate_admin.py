"""Recreate admin user with fresh password hash"""
from app.core.database import SessionLocal
from app.models.user import User
from passlib.context import CryptContext

# Use pbkdf2_sha256 only (bcrypt has issues on this system)
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

db = SessionLocal()

# Delete existing admin if exists
existing = db.query(User).filter(User.username == "admin").first()
if existing:
    print("Deleting existing admin user...")
    db.delete(existing)
    db.commit()

# Create new admin with fresh password hash
print("Creating new admin user...")
new_hash = pwd_context.hash("admin123")
print(f"New password hash: {new_hash[:60]}...")

admin_user = User(
    username="admin",
    email="admin@qpaper.ai",
    password_hash=new_hash,
    role="ADMIN",
    is_active=True
)

db.add(admin_user)
db.commit()

# Verify it works
user = db.query(User).filter(User.username == "admin").first()
verified = pwd_context.verify("admin123", user.password_hash)

print(f"\n✅ Admin user recreated!")
print(f"   Username: {user.username}")
print(f"   Role: {user.role}")
print(f"   Is Active: {user.is_active}")
print(f"   Password verified: {verified}")

if verified:
    print("\n🎉 Password verification works! Try logging in now.")
else:
    print("\n❌ Password verification failed - there's a deeper issue.")

db.close()


"""Test the exact authentication flow used by the API"""
from app.core.database import SessionLocal, get_db
from app.api.auth import authenticate_user, get_user, verify_password
from app.models.user import User
from passlib.context import CryptContext

# Test with a fresh database session (like the API does)
db = SessionLocal()

print("=" * 60)
print("Testing Authentication Flow")
print("=" * 60)

# Step 1: Get user
print("\n1. Getting user...")
user = get_user(db, "admin")
print(f"   User found: {user is not None}")
if user:
    print(f"   Username: {user.username}")
    print(f"   Role: {user.role}")
    print(f"   Is Active: {user.is_active}")
    print(f"   Password hash: {user.password_hash[:60]}...")

# Step 2: Test password verification directly
print("\n2. Testing password verification...")
if user:
    pwd_context = CryptContext(schemes=["bcrypt", "pbkdf2_sha256"], deprecated="auto")
    verified = pwd_context.verify("admin123", user.password_hash)
    print(f"   Password 'admin123' verified: {verified}")

# Step 3: Test authenticate_user function (exactly what API uses)
print("\n3. Testing authenticate_user function (API function)...")
result = authenticate_user(db, "admin", "admin123")
print(f"   Result: {result}")
if result:
    print(f"   ✅ Authentication successful!")
    print(f"   User: {result.username}, Role: {result.role}")
else:
    print(f"   ❌ Authentication failed!")

# Step 4: Test with wrong password
print("\n4. Testing with wrong password...")
result_wrong = authenticate_user(db, "admin", "wrongpassword")
print(f"   Result: {result_wrong}")
if not result_wrong:
    print(f"   ✅ Correctly rejected wrong password")

db.close()
print("\n" + "=" * 60)


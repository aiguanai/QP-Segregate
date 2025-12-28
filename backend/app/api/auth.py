from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from pydantic import BaseModel
from typing import Optional
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, stream=sys.stderr)
logger = logging.getLogger(__name__)

router = APIRouter()
logger.info("Auth router initialized")

# Password hashing - use pbkdf2_sha256 only (bcrypt has compatibility issues)
# pbkdf2_sha256 works reliably and is secure
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str = None

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str
    branch_id: Optional[int] = None
    academic_year: Optional[int] = None

class UserResponse(BaseModel):
    user_id: int
    username: str
    email: str
    role: str
    branch_id: Optional[int] = None
    academic_year: Optional[int] = None
    
    class Config:
        from_attributes = True

def verify_password(plain_password, hashed_password):
    """Verify password using pbkdf2_sha256"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        print(f"⚠️  Password verification error: {e}")
        return False

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db: Session, username: str):
    """Get user - simple query that avoids relationship loading"""
    try:
        # Simple query - SQLAlchemy will only load this user, not relationships
        # The relationships are lazy-loaded, so they won't trigger unless accessed
        return db.query(User).filter(User.username == username).first()
    except Exception as e:
        sys.stderr.write(f"❌ Error in get_user: {e}\n")
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        raise

def authenticate_user(db: Session, username: str, password: str):
    import sys
    try:
        user = get_user(db, username)
        if not user:
            print(f"❌ User '{username}' not found", file=sys.stderr)
            return False
        if not user.is_active:
            print(f"❌ User '{username}' is not active", file=sys.stderr)
            return False
        print(f"🔍 Verifying password for user '{username}'...", file=sys.stderr)
        print(f"   Password hash: {user.password_hash[:50]}...", file=sys.stderr)
        verified = verify_password(password, user.password_hash)
        print(f"   Password verified: {verified}", file=sys.stderr)
        if not verified:
            print(f"❌ Password verification failed for user '{username}'", file=sys.stderr)
            return False
        print(f"✅ Authentication successful for user '{username}'", file=sys.stderr)
        return user
    except Exception as e:
        print(f"❌ Authentication error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return False

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    import sys
    sys.stderr.write("=" * 60 + "\n")
    sys.stderr.write("🔐 get_current_user called\n")
    sys.stderr.flush()
    try:
        sys.stderr.write(f"   Token preview: {token[:30]}...\n")
        sys.stderr.flush()
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        username: str = payload.get("sub")
        sys.stderr.write(f"   Decoded username: {username}\n")
        sys.stderr.flush()
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError as e:
        sys.stderr.write(f"❌ JWT decode error: {e}\n")
        sys.stderr.flush()
        raise credentials_exception
    try:
        sys.stderr.write(f"   Calling get_user for: {token_data.username}\n")
        sys.stderr.flush()
        user = get_user(db, username=token_data.username)
        sys.stderr.write(f"   User found: {user is not None}\n")
        sys.stderr.flush()
        if user is None:
            sys.stderr.write("❌ User is None, raising credentials exception\n")
            sys.stderr.flush()
            raise credentials_exception
        sys.stderr.write(f"✅ Returning user: {user.username}\n")
        sys.stderr.flush()
        return user
    except HTTPException:
        raise
    except Exception as e:
        sys.stderr.write(f"❌ Error getting user: {e}\n")
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        raise HTTPException(status_code=500, detail=f"Error getting user: {str(e)}")

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = get_user(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password,
        role=user.role,
        branch_id=user.branch_id,
        academic_year=user.academic_year
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    logger.error("=" * 60)
    logger.error("🚀 LOGIN ENDPOINT CALLED")
    logger.error("=" * 60)
    sys.stderr.write("=" * 60 + "\n")
    sys.stderr.write("🚀 LOGIN ENDPOINT CALLED\n")
    sys.stderr.write("=" * 60 + "\n")
    sys.stderr.flush()
    try:
        logger.error(f"🔐 Login attempt - Username: '{form_data.username}', Password length: {len(form_data.password) if form_data.password else 0}")
        sys.stderr.write(f"🔐 Login attempt - Username: '{form_data.username}', Password length: {len(form_data.password) if form_data.password else 0}\n")
        sys.stderr.flush()
        user = authenticate_user(db, form_data.username, form_data.password)
        if not user:
            print(f"❌ Authentication failed for username: '{form_data.username}'", file=sys.stderr)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        # Log the error for debugging
        import traceback
        print(f"Login error: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    try:
        logger.error(f"✅ /me endpoint called for user: {current_user.username}")
        sys.stderr.write(f"✅ /me endpoint - User: {current_user.username}, Role: {current_user.role}\n")
        sys.stderr.flush()
        return current_user
    except Exception as e:
        logger.error(f"❌ Error in /me endpoint: {e}")
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/logout")
async def logout():
    return {"message": "Successfully logged out"}

@router.get("/test-auth")
async def test_auth(db: Session = Depends(get_db)):
    """Test endpoint to debug authentication"""
    try:
        user = get_user(db, "admin")
        if not user:
            return {"error": "Admin user not found", "user_exists": False}
        
        pwd_context = CryptContext(schemes=["bcrypt", "pbkdf2_sha256"], deprecated="auto")
        verified = pwd_context.verify("admin123", user.password_hash)
        
        return {
            "user_exists": True,
            "username": user.username,
            "is_active": user.is_active,
            "password_verified": verified,
            "password_hash_preview": user.password_hash[:50] + "...",
            "password_hash_scheme": user.password_hash.split("$")[1] if "$" in user.password_hash else "unknown"
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e), "traceback": traceback.format_exc()}

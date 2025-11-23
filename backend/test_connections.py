"""
Test script to verify all database connections
Run this to check if your cloud databases are properly configured

Make sure you have:
1. Activated your virtual environment: .\venv\Scripts\Activate.ps1
2. Installed dependencies: pip install -r requirements.txt
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Check if virtual environment is activated
try:
    import sqlalchemy
except ImportError:
    print("⚠️  WARNING: Virtual environment not activated or dependencies not installed!")
    print("   Please run:")
    print("   1. .\\venv\\Scripts\\Activate.ps1")
    print("   2. pip install -r requirements.txt")
    print()

def test_postgres():
    """Test PostgreSQL/Supabase connection"""
    print("🔍 Testing PostgreSQL connection...")
    try:
        from app.core.database import engine
        from sqlalchemy import text
        conn = engine.connect()
        result = conn.execute(text("SELECT version();"))
        version = result.fetchone()[0]
        print(f"✅ PostgreSQL connected successfully!")
        print(f"   Version: {version[:50]}...")
        conn.close()
        return True
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False

def test_mongodb():
    """Test MongoDB connection"""
    print("\n🔍 Testing MongoDB connection...")
    try:
        from app.core.config import settings
        from pymongo import MongoClient
        
        if not settings.MONGODB_URL:
            print("⚠️  MONGODB_URL not set in .env file")
            return False
        
        client = MongoClient(settings.MONGODB_URL, serverSelectionTimeoutMS=5000)
        # Test connection
        client.server_info()
        print("✅ MongoDB connected successfully!")
        client.close()
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False

def test_redis():
    """Test Redis connection"""
    print("\n🔍 Testing Redis connection...")
    try:
        from app.core.config import settings
        import redis
        
        if not settings.REDIS_URL:
            print("⚠️  REDIS_URL not set in .env file")
            return False
        
        r = redis.from_url(settings.REDIS_URL, socket_connect_timeout=5)
        r.ping()
        print("✅ Redis connected successfully!")
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False

def main():
    """Run all connection tests"""
    print("=" * 60)
    print("Database Connection Tests")
    print("=" * 60)
    
    results = {
        "PostgreSQL": test_postgres(),
        "MongoDB": test_mongodb(),
        "Redis": test_redis()
    }
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for db, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{db:15} {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 All database connections are working!")
    else:
        print("\n⚠️  Some connections failed. Please check your .env file.")
        print("   Required: DATABASE_URL (PostgreSQL)")
        print("   Optional: MONGODB_URL, REDIS_URL")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())


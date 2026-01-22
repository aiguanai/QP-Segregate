"""
Migration script to make password_hash nullable for OAuth users
Run with: python -m migrations.make_password_hash_nullable
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def migrate():
    """Make password_hash column nullable"""
    try:
        from app.core.database import engine
        from sqlalchemy import text
        
        print("🔄 Making password_hash column nullable...")
        
        with engine.connect() as conn:
            # Check current constraint
            result = conn.execute(text("""
                SELECT is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'password_hash'
            """))
            row = result.fetchone()
            
            if row and row[0] == 'NO':
                # Column is currently NOT NULL, make it nullable
                conn.execute(text("""
                    ALTER TABLE users 
                    ALTER COLUMN password_hash DROP NOT NULL
                """))
                conn.commit()
                print("✅ Successfully made password_hash nullable")
            else:
                print("ℹ️  password_hash is already nullable")
                
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you're running from the backend directory with venv activated:")
        print("   cd backend")
        print("   .\\venv\\Scripts\\activate  (Windows)")
        print("   python -m migrations.make_password_hash_nullable")
        raise
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise

if __name__ == "__main__":
    migrate()


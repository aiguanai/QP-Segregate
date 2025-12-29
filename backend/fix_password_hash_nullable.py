"""Fix password_hash column to be nullable for OAuth users"""
from app.core.database import engine
from sqlalchemy import text

def fix_password_hash():
    """Make password_hash column nullable for OAuth users"""
    try:
        with engine.connect() as conn:
            # Check current constraint
            result = conn.execute(text("""
                SELECT is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'password_hash'
            """))
            current_state = result.fetchone()
            
            if current_state and current_state[0] == 'NO':
                print("📝 Making password_hash column nullable...")
                conn.execute(text("ALTER TABLE users ALTER COLUMN password_hash DROP NOT NULL"))
                conn.commit()
                print("✅ password_hash column is now nullable")
            else:
                print("✅ password_hash column is already nullable")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_password_hash()


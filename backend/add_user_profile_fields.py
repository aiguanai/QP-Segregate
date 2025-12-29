"""Add profile_picture_url and display_name columns to users table"""
from app.core.database import engine
from sqlalchemy import text

def add_profile_fields():
    """Add profile_picture_url and display_name columns to users table"""
    try:
        with engine.connect() as conn:
            # Check if columns already exist
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name IN ('profile_picture_url', 'display_name')
            """))
            existing_columns = [row[0] for row in result.fetchall()]
            
            if 'profile_picture_url' not in existing_columns:
                print("📝 Adding profile_picture_url column...")
                conn.execute(text("ALTER TABLE users ADD COLUMN profile_picture_url VARCHAR(500)"))
                print("✅ Added profile_picture_url column")
            else:
                print("✅ profile_picture_url column already exists")
            
            if 'display_name' not in existing_columns:
                print("📝 Adding display_name column...")
                conn.execute(text("ALTER TABLE users ADD COLUMN display_name VARCHAR(100)"))
                print("✅ Added display_name column")
            else:
                print("✅ display_name column already exists")
            
            conn.commit()
            print("✅ All profile fields added successfully")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    add_profile_fields()


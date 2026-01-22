"""
Migration script to add profile_picture_url and display_name columns to users table
Run this script to update the database schema
"""
import sys
import os

# Add parent directory to path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine
from sqlalchemy import text

def add_user_profile_fields():
    """Add profile_picture_url and display_name columns to users table"""
    with engine.connect() as conn:
        # Add profile_picture_url column
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_picture_url VARCHAR(500)"))
            print("✅ Added profile_picture_url column")
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                print("⚠️  profile_picture_url column already exists")
            else:
                raise
        
        # Add display_name column
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS display_name VARCHAR(100)"))
            print("✅ Added display_name column")
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                print("⚠️  display_name column already exists")
            else:
                raise
        
        conn.commit()
        print("\n✅ Migration completed successfully!")

if __name__ == "__main__":
    add_user_profile_fields()


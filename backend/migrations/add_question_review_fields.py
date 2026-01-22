"""
Migration script to add topic_tags, is_reviewed, and review_status fields to questions table
Run this script to update the database schema

Usage:
    cd backend
    python migrations/add_question_review_fields.py
"""
import sys
import os

# Add parent directory to path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine
from sqlalchemy import text

def add_question_review_fields():
    """Add new fields to questions table"""
    with engine.connect() as conn:
        # Add topic_tags column (Text, nullable)
        try:
            conn.execute(text("ALTER TABLE questions ADD COLUMN topic_tags TEXT"))
            print("✅ Added topic_tags column")
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                print("⚠️  topic_tags column already exists")
            else:
                raise
        
        # Add is_reviewed column (Boolean, default False)
        try:
            conn.execute(text("ALTER TABLE questions ADD COLUMN is_reviewed BOOLEAN DEFAULT FALSE"))
            print("✅ Added is_reviewed column")
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                print("⚠️  is_reviewed column already exists")
            else:
                raise
        
        # Create review_status enum type
        try:
            conn.execute(text("CREATE TYPE reviewstatus AS ENUM ('PENDING', 'APPROVED', 'NEEDS_REVIEW')"))
            print("✅ Created reviewstatus enum type")
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                print("⚠️  reviewstatus enum type already exists")
            else:
                raise
        
        # Add review_status column
        try:
            conn.execute(text("ALTER TABLE questions ADD COLUMN review_status reviewstatus DEFAULT 'PENDING'"))
            print("✅ Added review_status column")
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                print("⚠️  review_status column already exists")
            else:
                raise
        
        conn.commit()
        print("\n✅ Migration completed successfully!")

if __name__ == "__main__":
    add_question_review_fields()


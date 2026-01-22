"""
Migration: Add student_course_selections table
This table stores student course selections
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine
from sqlalchemy import text

def run_migration():
    """Create student_course_selections table"""
    with engine.connect() as conn:
        # Create table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS student_course_selections (
                selection_id SERIAL PRIMARY KEY,
                student_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
                course_code VARCHAR(10) NOT NULL REFERENCES courses(course_code) ON DELETE CASCADE,
                selected_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(student_id, course_code)
            );
        """))
        
        # Create index
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_student_course_selections_student_id 
            ON student_course_selections(student_id);
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_student_course_selections_course_code 
            ON student_course_selections(course_code);
        """))
        
        conn.commit()
        print("✅ Migration completed: student_course_selections table created")

if __name__ == "__main__":
    run_migration()


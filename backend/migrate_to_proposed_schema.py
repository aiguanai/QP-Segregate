"""
Migration Script - Align Current Implementation with Proposed Schema
This script migrates the existing data to match the exact proposed database structure
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.proposed_schema import Semester, Subject, Unit, QPaper, Question
from app.models.course import Course, CourseUnit
from app.models.question_paper import QuestionPaper
from app.models.question import Question as OldQuestion
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_to_proposed_schema():
    """
    Migrate existing data to proposed schema structure
    """
    logger.info("🚀 Starting migration to proposed schema...")
    
    # Create database engine
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Step 1: Create proposed schema tables
        logger.info("📋 Creating proposed schema tables...")
        create_proposed_tables(engine)
        
        # Step 2: Migrate data from existing schema
        logger.info("🔄 Migrating data from existing schema...")
        migrate_data(db)
        
        # Step 3: Verify migration
        logger.info("✅ Verifying migration...")
        verify_migration(db)
        
        logger.info("🎉 Migration completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        db.rollback()
        raise e
    finally:
        db.close()

def create_proposed_tables(engine):
    """Create the proposed schema tables"""
    
    # Create tables using SQLAlchemy metadata
    from app.models.proposed_schema import Base
    Base.metadata.create_all(bind=engine)
    
    logger.info("✅ Proposed schema tables created")

def migrate_data(db):
    """Migrate data from existing schema to proposed schema"""
    
    # Step 1: Migrate Semesters
    logger.info("📚 Migrating semesters...")
    migrate_semesters(db)
    
    # Step 2: Migrate Subjects (from Courses)
    logger.info("📖 Migrating subjects...")
    migrate_subjects(db)
    
    # Step 3: Migrate Units
    logger.info("📝 Migrating units...")
    migrate_units(db)
    
    # Step 4: Migrate Question Papers
    logger.info("📄 Migrating question papers...")
    migrate_question_papers(db)
    
    # Step 5: Migrate Questions
    logger.info("❓ Migrating questions...")
    migrate_questions(db)

def migrate_semesters(db):
    """Create semesters from existing data"""
    
    # Create default semesters
    semesters = [
        Semester(sem_name="Semester 1"),
        Semester(sem_name="Semester 2"),
        Semester(sem_name="Semester 3"),
        Semester(sem_name="Semester 4"),
        Semester(sem_name="Semester 5"),
        Semester(sem_name="Semester 6"),
        Semester(sem_name="Semester 7"),
        Semester(sem_name="Semester 8")
    ]
    
    for semester in semesters:
        existing = db.query(Semester).filter(Semester.sem_name == semester.sem_name).first()
        if not existing:
            db.add(semester)
    
    db.commit()
    logger.info("✅ Semesters migrated")

def migrate_subjects(db):
    """Migrate courses to subjects"""
    
    # Get all existing courses
    courses = db.query(Course).all()
    
    # Get semester 1 as default
    semester_1 = db.query(Semester).filter(Semester.sem_name == "Semester 1").first()
    
    for course in courses:
        # Create subject from course
        subject = Subject(
            sub_name=course.course_name,
            sem_id=semester_1.sem_id  # Default to semester 1
        )
        
        # Check if subject already exists
        existing = db.query(Subject).filter(Subject.sub_name == subject.sub_name).first()
        if not existing:
            db.add(subject)
    
    db.commit()
    logger.info("✅ Subjects migrated")

def migrate_units(db):
    """Migrate course units to units"""
    
    # Get all course units
    course_units = db.query(CourseUnit).all()
    
    for course_unit in course_units:
        # Find corresponding subject
        subject = db.query(Subject).filter(Subject.sub_name.ilike(f"%{course_unit.course_code}%")).first()
        if not subject:
            # Create a generic subject if not found
            subject = Subject(
                sub_name=f"Course {course_unit.course_code}",
                sem_id=1  # Default to first semester
            )
            db.add(subject)
            db.commit()
        
        # Create unit
        unit = Unit(
            unit_name=course_unit.unit_name,
            sub_id=subject.sub_id
        )
        
        # Check if unit already exists
        existing = db.query(Unit).filter(
            Unit.unit_name == unit.unit_name,
            Unit.sub_id == unit.sub_id
        ).first()
        
        if not existing:
            db.add(unit)
    
    db.commit()
    logger.info("✅ Units migrated")

def migrate_question_papers(db):
    """Migrate question papers to QPaper"""
    
    # Get all existing question papers
    old_papers = db.query(QuestionPaper).all()
    
    for old_paper in old_papers:
        # Create QPaper
        qpaper = QPaper(
            paper_name=f"{old_paper.course_code} - {old_paper.exam_type.value}",
            file_link=old_paper.pdf_path or "",
            upload_date=old_paper.created_at,
            processing_status=old_paper.processing_status.value if old_paper.processing_status else "UPLOADED"
        )
        
        db.add(qpaper)
    
    db.commit()
    logger.info("✅ Question papers migrated")

def migrate_questions(db):
    """Migrate questions to proposed schema"""
    
    # Get all existing questions
    old_questions = db.query(OldQuestion).all()
    
    # Create mapping from old papers to new papers
    paper_mapping = {}
    old_papers = db.query(QuestionPaper).all()
    new_papers = db.query(QPaper).all()
    
    for i, old_paper in enumerate(old_papers):
        if i < len(new_papers):
            paper_mapping[old_paper.paper_id] = new_papers[i].paper_id
    
    # Create mapping from old units to new units
    unit_mapping = {}
    old_units = db.query(CourseUnit).all()
    new_units = db.query(Unit).all()
    
    for i, old_unit in enumerate(old_units):
        if i < len(new_units):
            unit_mapping[old_unit.unit_id] = new_units[i].unit_id
    
    for old_question in old_questions:
        # Create Question in proposed schema
        question = Question(
            ques_text=old_question.question_text,
            unit_id=unit_mapping.get(old_question.unit_id),
            paper_id=paper_mapping.get(old_question.paper_id),
            ai_tag=generate_ai_tag(old_question),
            confidence_score=old_question.classification_confidence or 0.0
        )
        
        db.add(question)
    
    db.commit()
    logger.info("✅ Questions migrated")

def generate_ai_tag(old_question):
    """Generate AI tag from existing question data"""
    tag_parts = []
    
    if old_question.bloom_level:
        tag_parts.append(f"Bloom:{old_question.bloom_level.value}")
    
    if old_question.difficulty_level:
        tag_parts.append(f"Difficulty:{old_question.difficulty_level.value}")
    
    if old_question.classification_confidence:
        if old_question.classification_confidence > 0.8:
            tag_parts.append("HighConfidence")
        elif old_question.classification_confidence > 0.5:
            tag_parts.append("MediumConfidence")
        else:
            tag_parts.append("LowConfidence")
    
    return "|".join(tag_parts) if tag_parts else "Unclassified"

def verify_migration(db):
    """Verify that migration was successful"""
    
    # Count records in each table
    semester_count = db.query(Semester).count()
    subject_count = db.query(Subject).count()
    unit_count = db.query(Unit).count()
    paper_count = db.query(QPaper).count()
    question_count = db.query(Question).count()
    
    logger.info(f"📊 Migration verification:")
    logger.info(f"   - Semesters: {semester_count}")
    logger.info(f"   - Subjects: {subject_count}")
    logger.info(f"   - Units: {unit_count}")
    logger.info(f"   - Papers: {paper_count}")
    logger.info(f"   - Questions: {question_count}")
    
    # Verify relationships
    questions_with_units = db.query(Question).filter(Question.unit_id.isnot(None)).count()
    questions_with_papers = db.query(Question).filter(Question.paper_id.isnot(None)).count()
    
    logger.info(f"   - Questions with units: {questions_with_units}")
    logger.info(f"   - Questions with papers: {questions_with_papers}")
    
    if question_count > 0:
        logger.info("✅ Migration verification successful!")
    else:
        logger.warning("⚠️ No questions found after migration")

def create_sample_data():
    """Create sample data to demonstrate the proposed system"""
    
    logger.info("🎯 Creating sample data for proposed system...")
    
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Create sample semester
        semester = Semester(sem_name="Computer Science - Semester 3")
        db.add(semester)
        db.commit()
        
        # Create sample subject
        subject = Subject(sub_name="Database Management Systems", sem_id=semester.sem_id)
        db.add(subject)
        db.commit()
        
        # Create sample units
        units = [
            Unit(unit_name="Introduction to Databases", sub_id=subject.sub_id),
            Unit(unit_name="SQL and Relational Algebra", sub_id=subject.sub_id),
            Unit(unit_name="Database Design and Normalization", sub_id=subject.sub_id)
        ]
        
        for unit in units:
            db.add(unit)
        db.commit()
        
        # Create sample question paper
        qpaper = QPaper(
            paper_name="DBMS Midterm Exam 2024",
            file_link="https://drive.google.com/sample-dbms-paper.pdf",
            processing_status="COMPLETED"
        )
        db.add(qpaper)
        db.commit()
        
        # Create sample questions
        sample_questions = [
            {
                "text": "What is a database management system?",
                "unit_name": "Introduction to Databases",
                "ai_tag": "Unit:Introduction to Databases|Bloom:Remembering|HighConfidence"
            },
            {
                "text": "Explain the difference between primary key and foreign key.",
                "unit_name": "SQL and Relational Algebra", 
                "ai_tag": "Unit:SQL and Relational Algebra|Bloom:Understanding|HighConfidence"
            },
            {
                "text": "Design a database schema for a library management system.",
                "unit_name": "Database Design and Normalization",
                "ai_tag": "Unit:Database Design and Normalization|Bloom:Creating|HighConfidence"
            }
        ]
        
        for sample_q in sample_questions:
            # Find corresponding unit
            unit = db.query(Unit).filter(Unit.unit_name == sample_q["unit_name"]).first()
            
            question = Question(
                ques_text=sample_q["text"],
                unit_id=unit.unit_id if unit else None,
                paper_id=qpaper.paper_id,
                ai_tag=sample_q["ai_tag"],
                confidence_score=0.9
            )
            db.add(question)
        
        db.commit()
        
        logger.info("✅ Sample data created successfully!")
        logger.info(f"   - Semester: {semester.sem_name}")
        logger.info(f"   - Subject: {subject.sub_name}")
        logger.info(f"   - Units: {len(units)}")
        logger.info(f"   - Paper: {qpaper.paper_name}")
        logger.info(f"   - Questions: {len(sample_questions)}")
        
    except Exception as e:
        logger.error(f"❌ Failed to create sample data: {e}")
        db.rollback()
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    print("🔄 QPaper AI - Migration to Proposed Schema")
    print("=" * 50)
    
    # Run migration
    migrate_to_proposed_schema()
    
    # Create sample data
    create_sample_data()
    
    print("\n🎉 Migration completed successfully!")
    print("The system is now aligned with the proposed schema.")
    print("\nNext steps:")
    print("1. Update your API endpoints to use the new schema")
    print("2. Test the automated ingestion pipeline")
    print("3. Verify the structured question bank functionality")

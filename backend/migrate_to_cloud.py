#!/usr/bin/env python3
"""
Database Migration Script for Cloud Setup
This script helps migrate your QPaper AI database to cloud services.
"""

import os
import sys
import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
import pymongo
from datetime import datetime

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.models import *
from app.core.config import settings

def check_cloud_connection():
    """Check if cloud database connections are working"""
    print("🔍 Checking cloud database connections...")
    
    # Check PostgreSQL
    try:
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ PostgreSQL connection successful")
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False
    
    # Check MongoDB
    try:
        client = pymongo.MongoClient(settings.MONGODB_URL)
        client.admin.command('ping')
        print("✅ MongoDB connection successful")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False
    
    return True

def create_database_schema():
    """Create all database tables"""
    print("📋 Creating database schema...")
    
    try:
        engine = create_engine(settings.DATABASE_URL)
        Base.metadata.create_all(bind=engine)
        print("✅ Database schema created successfully")
        return True
    except Exception as e:
        print(f"❌ Schema creation failed: {e}")
        return False

def create_initial_data():
    """Create initial data for the system"""
    print("📊 Creating initial data...")
    
    try:
        engine = create_engine(settings.DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Create password hasher
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # Create admin user
        admin_user = User(
            username="admin",
            email="admin@qpaper.ai",
            password_hash=pwd_context.hash("admin123"),
            role="ADMIN"
        )
        session.add(admin_user)
        print("✅ Admin user created (username: admin, password: admin123)")
        
        # Create sample student user
        student_user = User(
            username="student",
            email="student@qpaper.ai",
            password_hash=pwd_context.hash("student123"),
            role="STUDENT",
            branch_id=1,
            academic_year=3
        )
        session.add(student_user)
        print("✅ Student user created (username: student, password: student123)")
        
        # Create sample courses
        courses = [
            Course(
                course_code="CS301",
                course_name="Database Management Systems",
                credits=4,
                course_type="CORE",
                description="Introduction to database concepts, SQL, and database design"
            ),
            Course(
                course_code="CS302",
                course_name="Computer Networks",
                credits=4,
                course_type="CORE",
                description="Network protocols, TCP/IP, and network security"
            ),
            Course(
                course_code="CS303",
                course_name="Software Engineering",
                credits=4,
                course_type="CORE",
                description="Software development lifecycle and methodologies"
            ),
            Course(
                course_code="MA201",
                course_name="Mathematics",
                credits=3,
                course_type="CORE",
                description="Calculus, linear algebra, and discrete mathematics"
            ),
            Course(
                course_code="EC301",
                course_name="Digital Electronics",
                credits=4,
                course_type="CORE",
                description="Digital circuits, logic gates, and microprocessors"
            )
        ]
        
        for course in courses:
            session.add(course)
        print("✅ Sample courses created")
        
        # Create course units
        units = [
            # CS301 Units
            CourseUnit(
                course_code="CS301",
                unit_number=1,
                unit_name="Introduction to Databases",
                topics="Database concepts, data models, DBMS architecture, data independence"
            ),
            CourseUnit(
                course_code="CS301",
                unit_number=2,
                unit_name="SQL and Relational Algebra",
                topics="SQL queries, joins, subqueries, relational algebra operations"
            ),
            CourseUnit(
                course_code="CS301",
                unit_number=3,
                unit_name="Database Design and Normalization",
                topics="ER modeling, normalization forms, database design principles"
            ),
            CourseUnit(
                course_code="CS301",
                unit_number=4,
                unit_name="Transaction Management",
                topics="ACID properties, concurrency control, transaction isolation"
            ),
            CourseUnit(
                course_code="CS301",
                unit_number=5,
                unit_name="Database Security and Administration",
                topics="Access control, security policies, backup and recovery"
            ),
            
            # CS302 Units
            CourseUnit(
                course_code="CS302",
                unit_number=1,
                unit_name="Network Fundamentals",
                topics="OSI model, TCP/IP, network topologies, protocols"
            ),
            CourseUnit(
                course_code="CS302",
                unit_number=2,
                unit_name="Data Link Layer",
                topics="Error detection, flow control, MAC protocols, Ethernet"
            ),
            CourseUnit(
                course_code="CS302",
                unit_number=3,
                unit_name="Network Layer",
                topics="IP addressing, routing algorithms, IPv4/IPv6"
            ),
            CourseUnit(
                course_code="CS302",
                unit_number=4,
                unit_name="Transport Layer",
                topics="TCP, UDP, congestion control, reliability"
            ),
            CourseUnit(
                course_code="CS302",
                unit_number=5,
                unit_name="Application Layer",
                topics="HTTP, DNS, email protocols, network security"
            )
        ]
        
        for unit in units:
            session.add(unit)
        print("✅ Course units created")
        
        # Create course offerings
        offerings = [
            CourseOffering(
                course_code="CS301",
                branch_id=1,
                academic_year=3,
                semester_type="ODD"
            ),
            CourseOffering(
                course_code="CS302",
                branch_id=1,
                academic_year=3,
                semester_type="ODD"
            ),
            CourseOffering(
                course_code="CS303",
                branch_id=1,
                academic_year=3,
                semester_type="EVEN"
            ),
            CourseOffering(
                course_code="MA201",
                branch_id=1,
                academic_year=1,
                semester_type="ODD"
            ),
            CourseOffering(
                course_code="EC301",
                branch_id=2,
                academic_year=2,
                semester_type="ODD"
            )
        ]
        
        for offering in offerings:
            session.add(offering)
        print("✅ Course offerings created")
        
        # Create course equivalences
        equivalences = [
            CourseEquivalence(
                primary_course_code="CS301",
                equivalent_course_code="IT301",
                reason="Same content, different department"
            ),
            CourseEquivalence(
                primary_course_code="CS302",
                equivalent_course_code="EC302",
                reason="Network fundamentals overlap"
            )
        ]
        
        for equivalence in equivalences:
            session.add(equivalence)
        print("✅ Course equivalences created")
        
        session.commit()
        session.close()
        
        print("✅ Initial data created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Initial data creation failed: {e}")
        if 'session' in locals():
            session.rollback()
            session.close()
        return False

def setup_mongodb_collections():
    """Setup MongoDB collections with initial data"""
    print("🍃 Setting up MongoDB collections...")
    
    try:
        client = pymongo.MongoClient(settings.MONGODB_URL)
        db = client.qpaper_ai
        
        # Create indexes for better performance
        collections_to_index = [
            ('raw_ocr_data', 'paper_id'),
            ('syllabus_documents', 'course_code'),
            ('question_embeddings', 'question_id'),
            ('processing_errors', 'paper_id')
        ]
        
        for collection_name, index_field in collections_to_index:
            collection = db[collection_name]
            collection.create_index(index_field)
            print(f"✅ Index created for {collection_name}.{index_field}")
        
        # Insert sample syllabus documents
        syllabus_docs = [
            {
                'course_code': 'CS301',
                'version': '2024',
                'units': [
                    {
                        'unit_id': 1,
                        'name': 'Introduction to Databases',
                        'topics': 'Database concepts, data models, DBMS architecture, data independence, database users, database administrator'
                    },
                    {
                        'unit_id': 2,
                        'name': 'SQL and Relational Algebra',
                        'topics': 'SQL queries, joins, subqueries, relational algebra operations, SQL functions, views'
                    },
                    {
                        'unit_id': 3,
                        'name': 'Database Design and Normalization',
                        'topics': 'ER modeling, normalization forms, database design principles, functional dependencies'
                    }
                ],
                'created_at': datetime.utcnow()
            }
        ]
        
        for doc in syllabus_docs:
            db.syllabus_documents.replace_one(
                {'course_code': doc['course_code']},
                doc,
                upsert=True
            )
        
        print("✅ MongoDB collections setup complete")
        return True
        
    except Exception as e:
        print(f"❌ MongoDB setup failed: {e}")
        return False

def verify_setup():
    """Verify that the setup is working correctly"""
    print("🔍 Verifying setup...")
    
    try:
        engine = create_engine(settings.DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Check if tables exist and have data
        user_count = session.query(User).count()
        course_count = session.query(Course).count()
        unit_count = session.query(CourseUnit).count()
        
        print(f"✅ Users: {user_count}")
        print(f"✅ Courses: {course_count}")
        print(f"✅ Units: {unit_count}")
        
        # Check MongoDB
        client = pymongo.MongoClient(settings.MONGODB_URL)
        db = client.qpaper_ai
        syllabus_count = db.syllabus_documents.count_documents({})
        print(f"✅ Syllabus documents: {syllabus_count}")
        
        session.close()
        print("✅ Setup verification complete")
        return True
        
    except Exception as e:
        print(f"❌ Setup verification failed: {e}")
        return False

def main():
    """Main migration function"""
    print("🚀 QPaper AI Cloud Migration Script")
    print("=" * 50)
    
    # Check if cloud URLs are configured
    if not settings.DATABASE_URL or 'localhost' in settings.DATABASE_URL:
        print("❌ Please configure cloud database URLs in your .env file")
        print("   Set CLOUD_DATABASE_URL, CLOUD_MONGODB_URL, and CLOUD_REDIS_URL")
        return False
    
    # Step 1: Check connections
    if not check_cloud_connection():
        print("❌ Cloud database connections failed. Please check your configuration.")
        return False
    
    # Step 2: Create schema
    if not create_database_schema():
        print("❌ Database schema creation failed.")
        return False
    
    # Step 3: Create initial data
    if not create_initial_data():
        print("❌ Initial data creation failed.")
        return False
    
    # Step 4: Setup MongoDB
    if not setup_mongodb_collections():
        print("❌ MongoDB setup failed.")
        return False
    
    # Step 5: Verify setup
    if not verify_setup():
        print("❌ Setup verification failed.")
        return False
    
    print("\n🎉 Cloud migration completed successfully!")
    print("\n📋 Next steps:")
    print("1. Start your application: docker-compose -f docker-compose.cloud.yml up")
    print("2. Access the application at http://localhost:3000")
    print("3. Login with admin/admin123 or student/student123")
    print("4. Upload your first question paper!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

import os
from app.core.database import Base, engine
from app.models import Branch, User, Course
from passlib.context import CryptContext
from sqlalchemy.orm import sessionmaker

def init_database():
    """Initialize database with schema and initial data"""
    
    print("📋 Creating database schema...")
    Base.metadata.create_all(bind=engine)
    print("✅ Schema created")
    
    # Create session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Create sample branches first
        print("🏛️  Creating sample branches...")
        sample_branches = [
            Branch(branch_name="Computer Science", branch_code="CS"),
            Branch(branch_name="Electronics and Communication", branch_code="EC"),
            Branch(branch_name="Mechanical Engineering", branch_code="ME"),
        ]
        
        branches_created = 0
        for branch in sample_branches:
            existing = session.query(Branch).filter(Branch.branch_code == branch.branch_code).first()
            if not existing:
                session.add(branch)
                branches_created += 1
        
        session.commit()
        if branches_created > 0:
            print(f"✅ Created {branches_created} sample branches")
        else:
            print("⚠️  Sample branches already exist")
        
        # Get or create first branch for student user
        first_branch = session.query(Branch).first()
        if not first_branch:
            first_branch = Branch(branch_name="Computer Science", branch_code="CS")
            session.add(first_branch)
            session.commit()
            session.refresh(first_branch)
        
        # Check if admin exists
        admin = session.query(User).filter(User.username == "admin").first()
        if admin:
            print("⚠️  Admin user already exists")
        else:
            # Create admin user
            # Try bcrypt first, fallback to pbkdf2_sha256 if bcrypt fails
            try:
                pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
                password_hash = pwd_context.hash("admin123")
            except Exception as e:
                print(f"⚠️  Bcrypt failed ({e}), using pbkdf2_sha256 instead")
                pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
                password_hash = pwd_context.hash("admin123")
            
            admin_user = User(
                username="admin",
                email="admin@qpaper.ai",
                password_hash=password_hash,
                role="ADMIN"
            )
            session.add(admin_user)
            session.commit()
            print("✅ Admin user created (username: admin, password: admin123)")
        
        # Check if student exists
        student = session.query(User).filter(User.username == "student").first()
        if student:
            print("⚠️  Student user already exists")
        else:
            # Create student user
            try:
                pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
                password_hash = pwd_context.hash("student123")
            except Exception as e:
                print(f"⚠️  Bcrypt failed ({e}), using pbkdf2_sha256 instead")
                pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
                password_hash = pwd_context.hash("student123")
            
            student_user = User(
                username="student",
                email="student@rvce.edu.in",
                password_hash=password_hash,
                role="STUDENT",
                branch_id=first_branch.branch_id,
                academic_year=3
            )
            session.add(student_user)
            session.commit()
            print("✅ Student user created (username: student, password: student123)")
        
        # Create sample courses
        courses = [
            Course(course_code="CS301", course_name="Database Management Systems", credits=4, course_type="CORE"),
            Course(course_code="CS302", course_name="Computer Networks", credits=4, course_type="CORE"),
        ]
        
        for course in courses:
            existing = session.query(Course).filter(Course.course_code == course.course_code).first()
            if not existing:
                session.add(course)
        
        session.commit()
        print("✅ Sample courses created")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    init_database()
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.course import Course, CourseUnit, CourseOffering
from app.models.user import User
from app.models.question_paper import QuestionPaper, ProcessingStatus, ExamType, SemesterType
from app.api.auth import get_current_user
from app.utils.activity_logger import log_activity
from pydantic import BaseModel
import os
import shutil
from datetime import datetime

router = APIRouter()

class CourseResponse(BaseModel):
    course_code: str
    course_name: str
    credits: int
    course_type: str
    description: Optional[str] = None
    
    class Config:
        from_attributes = True

class CourseUnitResponse(BaseModel):
    unit_id: int
    unit_number: int
    unit_name: str
    topics: Optional[str] = None
    
    class Config:
        from_attributes = True

class CourseCreate(BaseModel):
    course_code: str
    course_name: str
    credits: int
    course_type: str  # CORE, ELECTIVE, LAB
    description: Optional[str] = None

class CourseUpdate(BaseModel):
    course_name: Optional[str] = None
    credits: Optional[int] = None
    course_type: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

@router.get("/", response_model=List[CourseResponse])
async def get_courses(
    branch_id: Optional[int] = Query(None),
    year: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Get courses with optional filtering by branch and year"""
    query = db.query(Course).filter(Course.is_active == True)
    
    if branch_id and year:
        # Get courses for specific branch and year
        query = query.join(CourseOffering).filter(
            CourseOffering.branch_id == branch_id,
            CourseOffering.academic_year == year,
            CourseOffering.is_active == True
        )
    
    courses = query.all()
    return courses

@router.get("/{course_code}/units", response_model=List[CourseUnitResponse])
async def get_course_units(
    course_code: str,
    db: Session = Depends(get_db)
):
    """Get units for a specific course"""
    course = db.query(Course).filter(Course.course_code == course_code).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    units = db.query(CourseUnit).filter(
        CourseUnit.course_code == course_code,
        CourseUnit.is_active == True
    ).order_by(CourseUnit.unit_number).all()
    
    return units

@router.get("/{course_code}", response_model=CourseResponse)
async def get_course(
    course_code: str,
    db: Session = Depends(get_db)
):
    """Get specific course details"""
    course = db.query(Course).filter(Course.course_code == course_code).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    return course

@router.post("/", response_model=CourseResponse)
async def create_course(
    course_code: str = Form(...),
    course_name: str = Form(...),
    credits: int = Form(...),
    course_type: str = Form(...),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new course (admin only) with optional syllabus upload"""
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Check if course already exists
    existing_course = db.query(Course).filter(Course.course_code == course_code.upper()).first()
    if existing_course:
        raise HTTPException(status_code=400, detail=f"Course with code {course_code} already exists")
    
    # Validate course_type
    valid_types = ['CORE', 'ELECTIVE', 'LAB']
    if course_type.upper() not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid course_type. Must be one of: {', '.join(valid_types)}"
        )
    
    # Create course
    new_course = Course(
        course_code=course_code.upper(),
        course_name=course_name,
        credits=credits,
        course_type=course_type.upper(),
        description=description,
        is_active=True
    )
    
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    
    # Log activity
    log_activity(
        db=db,
        user_id=current_user.user_id,
        activity_type="COURSE_CREATED",
        description=f"Created course {new_course.course_code}: {new_course.course_name}",
        entity_type="course",
        entity_id=new_course.course_code,
        metadata={
            "course_code": new_course.course_code,
            "course_name": new_course.course_name,
            "credits": new_course.credits,
            "course_type": new_course.course_type
        }
    )
    
    return new_course

@router.put("/{course_code}", response_model=CourseResponse)
async def update_course(
    course_code: str,
    syllabus_file: Optional[UploadFile] = File(None),
    academic_year: Optional[int] = Form(None),
    semester_type: Optional[str] = Form(None),
    course_name: Optional[str] = Form(None),
    credits: Optional[int] = Form(None),
    course_type: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    is_active: Optional[bool] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an existing course (admin only) with optional syllabus update"""
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    course = db.query(Course).filter(Course.course_code == course_code).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Handle course metadata updates (from Form data)
    changes = []
    
    if course_name is not None:
        course.course_name = course_name
        changes.append(f"name: {course_name}")
    
    if credits is not None:
        course.credits = credits
        changes.append(f"credits: {credits}")
    
    if course_type is not None:
        valid_types = ['CORE', 'ELECTIVE', 'LAB']
        if course_type.upper() not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid course_type. Must be one of: {', '.join(valid_types)}"
            )
        course.course_type = course_type.upper()
        changes.append(f"type: {course_type}")
    
    if description is not None:
        course.description = description
        changes.append("description updated")
    
    if is_active is not None:
        course.is_active = is_active
        changes.append(f"active: {is_active}")
    
    # Handle syllabus update if provided
    if syllabus_file is not None:
        # Validate syllabus file
        filename_lower = syllabus_file.filename.lower() if syllabus_file.filename else ""
        if not (filename_lower.endswith('.pdf') or filename_lower.endswith('.docx') or filename_lower.endswith('.doc')):
            raise HTTPException(status_code=400, detail="Syllabus file must be PDF or DOCX")
        
        # Validate academic_year and semester_type if syllabus is provided
        if academic_year is None or semester_type is None:
            raise HTTPException(
                status_code=400,
                detail="academic_year and semester_type are required when updating syllabus"
            )
        
        # Validate semester_type
        if semester_type.upper() not in ['ODD', 'EVEN']:
            raise HTTPException(status_code=400, detail="Semester type must be ODD or EVEN")
        
        # Save new syllabus file
        upload_id = f"syllabus_{course_code.upper()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        permanent_dir = "storage/papers"
        os.makedirs(permanent_dir, exist_ok=True)
        
        # Determine file extension
        file_ext = '.pdf'
        if filename_lower.endswith('.docx') or filename_lower.endswith('.doc'):
            file_ext = '.docx' if filename_lower.endswith('.docx') else '.doc'
        
        syllabus_path = os.path.join(permanent_dir, f"{upload_id}{file_ext}")
        
        # Save file
        with open(syllabus_path, "wb") as buffer:
            shutil.copyfileobj(syllabus_file.file, buffer)
        
        # Find existing syllabus (QuestionPaper with exam_type=SEE for this course)
        existing_syllabus = db.query(QuestionPaper).filter(
            QuestionPaper.course_code == course_code,
            QuestionPaper.exam_type == ExamType.SEE
        ).first()
        
        if existing_syllabus:
            # Update existing syllabus
            # Delete old file if it exists
            if existing_syllabus.pdf_path and os.path.exists(existing_syllabus.pdf_path):
                try:
                    os.remove(existing_syllabus.pdf_path)
                except Exception as e:
                    pass  # Continue even if file deletion fails
            
            existing_syllabus.pdf_path = syllabus_path
            existing_syllabus.academic_year = academic_year
            existing_syllabus.semester_type = SemesterType(semester_type.upper())
            existing_syllabus.file_size = os.path.getsize(syllabus_path)
            existing_syllabus.uploaded_by = current_user.user_id
            changes.append(f"syllabus updated (Year {academic_year}, {semester_type})")
        else:
            # Create new syllabus entry
            new_syllabus = QuestionPaper(
                course_code=course_code,
                academic_year=academic_year,
                semester_type=SemesterType(semester_type.upper()),
                exam_type=ExamType.SEE,
                pdf_path=syllabus_path,
                uploaded_by=current_user.user_id,
                processing_status=ProcessingStatus.COMPLETED,
                processing_progress=100,
                total_questions_extracted=0,
                file_size=os.path.getsize(syllabus_path)
            )
            db.add(new_syllabus)
            changes.append(f"syllabus added (Year {academic_year}, {semester_type})")
    
    db.commit()
    db.refresh(course)
    
    # Log activity
    log_activity(
        db=db,
        user_id=current_user.user_id,
        activity_type="COURSE_UPDATED",
        description=f"Updated course {course_code}: {', '.join(changes) if changes else 'No changes'}",
        entity_type="course",
        entity_id=course_code,
        metadata={"course_code": course_code, "changes": changes}
    )
    
    return course

@router.delete("/{course_code}")
async def delete_course(
    course_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a course (admin only) - soft delete by setting is_active=False"""
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    course = db.query(Course).filter(Course.course_code == course_code).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Soft delete: set is_active to False instead of hard deleting
    # This preserves data integrity with related records
    course.is_active = False
    db.commit()
    
    # Log activity
    log_activity(
        db=db,
        user_id=current_user.user_id,
        activity_type="COURSE_DELETED",
        description=f"Deleted course {course_code}: {course.course_name}",
        entity_type="course",
        entity_id=course_code,
        metadata={"course_code": course_code, "course_name": course.course_name}
    )
    
    return {"message": f"Course {course_code} deleted successfully"}

class UnitCreate(BaseModel):
    unit_number: int
    unit_name: str
    topics: Optional[str] = None  # Can be JSON string or comma-separated text

class UnitUpdate(BaseModel):
    unit_number: Optional[int] = None
    unit_name: Optional[str] = None
    topics: Optional[str] = None
    is_active: Optional[bool] = None

@router.post("/{course_code}/units", response_model=CourseUnitResponse)
async def create_unit(
    course_code: str,
    unit: UnitCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new unit for a course (admin only)"""
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Verify course exists
    course = db.query(Course).filter(Course.course_code == course_code.upper()).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Check if unit number already exists for this course
    existing = db.query(CourseUnit).filter(
        CourseUnit.course_code == course_code.upper(),
        CourseUnit.unit_number == unit.unit_number,
        CourseUnit.is_active == True
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Unit {unit.unit_number} already exists for course {course_code}"
        )
    
    # Create unit
    new_unit = CourseUnit(
        course_code=course_code.upper(),
        unit_number=unit.unit_number,
        unit_name=unit.unit_name,
        topics=unit.topics,  # Store as text (can be JSON string or plain text)
        is_active=True
    )
    
    db.add(new_unit)
    db.commit()
    db.refresh(new_unit)
    
    # Log activity
    log_activity(
        db=db,
        user_id=current_user.user_id,
        activity_type="UNIT_CREATED",
        description=f"Created unit {unit.unit_number} for course {course_code}: {unit.unit_name}",
        entity_type="unit",
        entity_id=str(new_unit.unit_id),
        metadata={
            "course_code": course_code,
            "unit_number": unit.unit_number,
            "unit_name": unit.unit_name
        }
    )
    
    return new_unit

@router.put("/{course_code}/units/{unit_id}", response_model=CourseUnitResponse)
async def update_unit(
    course_code: str,
    unit_id: int,
    unit: UnitUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a unit (admin only)"""
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Verify course exists
    course = db.query(Course).filter(Course.course_code == course_code.upper()).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Get unit
    db_unit = db.query(CourseUnit).filter(
        CourseUnit.unit_id == unit_id,
        CourseUnit.course_code == course_code.upper()
    ).first()
    
    if not db_unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    
    # Check if updating unit_number would conflict
    if unit.unit_number is not None and unit.unit_number != db_unit.unit_number:
        existing = db.query(CourseUnit).filter(
            CourseUnit.course_code == course_code.upper(),
            CourseUnit.unit_number == unit.unit_number,
            CourseUnit.unit_id != unit_id,
            CourseUnit.is_active == True
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Unit {unit.unit_number} already exists for course {course_code}"
            )
    
    # Update fields
    changes = []
    if unit.unit_number is not None:
        db_unit.unit_number = unit.unit_number
        changes.append(f"unit_number: {unit.unit_number}")
    if unit.unit_name is not None:
        db_unit.unit_name = unit.unit_name
        changes.append(f"unit_name: {unit.unit_name}")
    if unit.topics is not None:
        db_unit.topics = unit.topics
        changes.append("topics updated")
    if unit.is_active is not None:
        db_unit.is_active = unit.is_active
        changes.append(f"is_active: {unit.is_active}")
    
    db.commit()
    db.refresh(db_unit)
    
    # Log activity
    log_activity(
        db=db,
        user_id=current_user.user_id,
        activity_type="UNIT_UPDATED",
        description=f"Updated unit {db_unit.unit_number} for course {course_code}: {', '.join(changes)}",
        entity_type="unit",
        entity_id=str(unit_id),
        metadata={
            "course_code": course_code,
            "unit_id": unit_id,
            "changes": changes
        }
    )
    
    return db_unit

@router.delete("/{course_code}/units/{unit_id}")
async def delete_unit(
    course_code: str,
    unit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a unit (admin only) - soft delete"""
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get unit
    unit = db.query(CourseUnit).filter(
        CourseUnit.unit_id == unit_id,
        CourseUnit.course_code == course_code.upper()
    ).first()
    
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    
    # Soft delete
    unit.is_active = False
    db.commit()
    
    # Log activity
    log_activity(
        db=db,
        user_id=current_user.user_id,
        activity_type="UNIT_DELETED",
        description=f"Deleted unit {unit.unit_number} for course {course_code}: {unit.unit_name}",
        entity_type="unit",
        entity_id=str(unit_id),
        metadata={
            "course_code": course_code,
            "unit_number": unit.unit_number,
            "unit_name": unit.unit_name
        }
    )
    
    return {"message": f"Unit {unit.unit_number} deleted successfully"}
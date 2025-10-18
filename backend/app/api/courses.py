from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.course import Course, CourseUnit, CourseOffering
from app.models.user import User
from app.api.auth import get_current_user
from pydantic import BaseModel

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

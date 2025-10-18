from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.user import User
from app.models.question import Question, StudentBookmark
from app.models.question_paper import QuestionPaper
from app.models.course import Course, CourseEquivalence, CourseOffering
from app.api.auth import get_current_user
from pydantic import BaseModel

router = APIRouter()

class SearchRequest(BaseModel):
    query: str
    filters: Optional[dict] = {}
    page: int = 1
    limit: int = 20

class SearchFilters(BaseModel):
    course_codes: Optional[List[str]] = None
    unit_ids: Optional[List[int]] = None
    marks_min: Optional[int] = None
    marks_max: Optional[int] = None
    bloom_levels: Optional[List[int]] = None
    exam_types: Optional[List[str]] = None
    year_from: Optional[int] = None
    year_to: Optional[int] = None

class QuestionResponse(BaseModel):
    question_id: int
    question_text: str
    marks: Optional[int]
    bloom_level: Optional[int]
    bloom_category: Optional[str]
    difficulty_level: Optional[str]
    course_code: str
    unit_name: Optional[str]
    exam_type: str
    academic_year: int
    semester_type: str
    exam_date: Optional[str]
    variant_count: int = 0
    
    class Config:
        from_attributes = True

class RandomQuestionsRequest(BaseModel):
    course_code: str
    unit_ids: Optional[List[int]] = None
    count: int = 10
    bloom_levels: Optional[List[int]] = None

@router.get("/my-courses")
async def get_my_courses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get courses for student's branch and academic year"""
    if current_user.role != "STUDENT":
        raise HTTPException(status_code=403, detail="Student access required")
    
    # Get courses for student's branch and year
    courses = db.query(Course).join(CourseOffering).filter(
        CourseOffering.branch_id == current_user.branch_id,
        CourseOffering.academic_year == current_user.academic_year,
        CourseOffering.is_active == True
    ).all()
    
    return courses

@router.post("/search")
async def search_questions(
    request: SearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search questions with semantic search"""
    if current_user.role != "STUDENT":
        raise HTTPException(status_code=403, detail="Student access required")
    
    # Build query with filters
    query = db.query(Question).join(QuestionPaper).filter(Question.is_canonical == True)
    
    # Apply filters
    if request.filters.get("course_codes"):
        # Include equivalent courses
        course_codes = request.filters["course_codes"]
        equivalent_courses = []
        for course_code in course_codes:
            # Get equivalent courses
            equivalences = db.query(CourseEquivalence).filter(
                (CourseEquivalence.primary_course_code == course_code) |
                (CourseEquivalence.equivalent_course_code == course_code)
            ).all()
            for eq in equivalences:
                if eq.primary_course_code == course_code:
                    equivalent_courses.append(eq.equivalent_course_code)
                else:
                    equivalent_courses.append(eq.primary_course_code)
        
        all_courses = course_codes + equivalent_courses
        query = query.filter(Question.course_code.in_(all_courses))
    
    if request.filters.get("unit_ids"):
        query = query.filter(Question.unit_id.in_(request.filters["unit_ids"]))
    
    if request.filters.get("marks_min"):
        query = query.filter(Question.marks >= request.filters["marks_min"])
    
    if request.filters.get("marks_max"):
        query = query.filter(Question.marks <= request.filters["marks_max"])
    
    if request.filters.get("bloom_levels"):
        query = query.filter(Question.bloom_level.in_(request.filters["bloom_levels"]))
    
    if request.filters.get("exam_types"):
        query = query.filter(QuestionPaper.exam_type.in_(request.filters["exam_types"]))
    
    if request.filters.get("year_from"):
        query = query.filter(QuestionPaper.academic_year >= request.filters["year_from"])
    
    if request.filters.get("year_to"):
        query = query.filter(QuestionPaper.academic_year <= request.filters["year_to"])
    
    # TODO: Implement semantic search using embeddings
    # For now, use text search
    if request.query:
        query = query.filter(Question.question_text.ilike(f"%{request.query}%"))
    
    # Pagination
    offset = (request.page - 1) * request.limit
    questions = query.offset(offset).limit(request.limit).all()
    
    # Convert to response format
    results = []
    for q in questions:
        # Count variants
        variant_count = db.query(Question).filter(
            Question.parent_question_id == q.question_id
        ).count()
        
        results.append(QuestionResponse(
            question_id=q.question_id,
            question_text=q.question_text,
            marks=q.marks,
            bloom_level=q.bloom_level.value if q.bloom_level else None,
            bloom_category=q.bloom_category.value if q.bloom_category else None,
            difficulty_level=q.difficulty_level.value if q.difficulty_level else None,
            course_code=q.course_code,
            unit_name=q.unit.unit_name if q.unit else None,
            exam_type=q.paper.exam_type.value,
            academic_year=q.paper.academic_year,
            semester_type=q.paper.semester_type.value,
            exam_date=q.paper.exam_date.isoformat() if q.paper.exam_date else None,
            variant_count=variant_count
        ))
    
    return {
        "questions": results,
        "total": query.count(),
        "page": request.page,
        "limit": request.limit
    }

@router.get("/question/{question_id}/variants")
async def get_question_variants(
    question_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get variant questions for a canonical question"""
    if current_user.role != "STUDENT":
        raise HTTPException(status_code=403, detail="Student access required")
    
    # Get canonical question
    canonical = db.query(Question).filter(Question.question_id == question_id).first()
    if not canonical:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Get variants
    variants = db.query(Question).filter(Question.parent_question_id == question_id).all()
    
    return {
        "canonical": canonical,
        "variants": variants
    }

@router.post("/bookmark/{question_id}")
async def bookmark_question(
    question_id: int,
    notes: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Bookmark a question"""
    if current_user.role != "STUDENT":
        raise HTTPException(status_code=403, detail="Student access required")
    
    # Check if question exists
    question = db.query(Question).filter(Question.question_id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Check if already bookmarked
    existing = db.query(StudentBookmark).filter(
        StudentBookmark.student_id == current_user.user_id,
        StudentBookmark.question_id == question_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Question already bookmarked")
    
    # Create bookmark
    bookmark = StudentBookmark(
        student_id=current_user.user_id,
        question_id=question_id,
        notes=notes
    )
    
    db.add(bookmark)
    db.commit()
    
    return {"message": "Question bookmarked successfully"}

@router.get("/bookmarks")
async def get_bookmarks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get student's bookmarked questions"""
    if current_user.role != "STUDENT":
        raise HTTPException(status_code=403, detail="Student access required")
    
    bookmarks = db.query(StudentBookmark).filter(
        StudentBookmark.student_id == current_user.user_id
    ).all()
    
    return bookmarks

@router.post("/random-questions")
async def get_random_questions(
    request: RandomQuestionsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get random questions for practice"""
    if current_user.role != "STUDENT":
        raise HTTPException(status_code=403, detail="Student access required")
    
    # Build query
    query = db.query(Question).join(QuestionPaper).filter(
        Question.is_canonical == True,
        Question.course_code == request.course_code
    )
    
    if request.unit_ids:
        query = query.filter(Question.unit_id.in_(request.unit_ids))
    
    if request.bloom_levels:
        query = query.filter(Question.bloom_level.in_(request.bloom_levels))
    
    # Get random questions
    questions = query.order_by(db.func.random()).limit(request.count).all()
    
    return questions

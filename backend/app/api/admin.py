from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os
import shutil
from app.core.database import get_db
from app.models.user import User
from app.models.question_paper import QuestionPaper, ProcessingStatus, ExamType, SemesterType
from app.models.question import Question, ReviewQueue
from app.api.auth import get_current_user
from app.services.ocr_service import OCRService
from app.services.classification_service import ClassificationService
from app.tasks.processing import process_question_paper
from pydantic import BaseModel

router = APIRouter()

class PDFUploadResponse(BaseModel):
    upload_id: str
    page_count: int
    file_size: int
    temp_path: str

class MetadataSubmitRequest(BaseModel):
    upload_id: str
    course_code: str
    academic_year: int
    semester_type: str
    exam_type: str
    exam_date: Optional[datetime] = None

class ProcessingStatusResponse(BaseModel):
    paper_id: int
    status: str
    progress: float
    questions_extracted: int
    errors: List[str] = []

class ReviewQueueItem(BaseModel):
    review_id: int
    question_id: int
    question_text: str
    issue_type: str
    suggested_correction: dict
    priority: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class QuestionApprovalRequest(BaseModel):
    unit_id: Optional[int] = None
    bloom_level: Optional[int] = None
    marks: Optional[int] = None
    approved: bool = True

@router.post("/upload-pdf", response_model=PDFUploadResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Step 1: Upload PDF file and return upload details"""
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Create upload ID and temp directory
    upload_id = f"upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
    temp_dir = "tmp/uploads"
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, upload_id)
    
    # Save file to temp location
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Get file size
    file_size = os.path.getsize(temp_path)
    
    # Get page count using pdf2image
    try:
        from pdf2image import convert_from_path
        pages = convert_from_path(temp_path, first_page=1, last_page=1)
        page_count = len(convert_from_path(temp_path))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading PDF: {str(e)}")
    
    return PDFUploadResponse(
        upload_id=upload_id,
        page_count=page_count,
        file_size=file_size,
        temp_path=temp_path
    )

@router.post("/submit-metadata")
async def submit_metadata(
    request: MetadataSubmitRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Step 2: Submit metadata and start processing"""
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Check if temp file exists
    temp_path = os.path.join("tmp/uploads", request.upload_id)
    if not os.path.exists(temp_path):
        raise HTTPException(status_code=404, detail="Upload file not found")
    
    # Create permanent storage path
    permanent_dir = "storage/papers"
    os.makedirs(permanent_dir, exist_ok=True)
    permanent_path = os.path.join(permanent_dir, f"{request.upload_id}.pdf")
    
    # Move file to permanent storage
    shutil.move(temp_path, permanent_path)
    
    # Create database entry
    paper = QuestionPaper(
        course_code=request.course_code,
        academic_year=request.academic_year,
        semester_type=SemesterType(request.semester_type),
        exam_type=ExamType(request.exam_type),
        exam_date=request.exam_date,
        pdf_path=permanent_path,
        temp_pdf_path=temp_path,
        uploaded_by=current_user.user_id,
        processing_status=ProcessingStatus.METADATA_PENDING,
        file_size=os.path.getsize(permanent_path)
    )
    
    db.add(paper)
    db.commit()
    db.refresh(paper)
    
    # Start background processing
    task = process_question_paper.delay(paper.paper_id)
    
    return {
        "paper_id": paper.paper_id,
        "task_id": task.id,
        "message": "Processing started"
    }

@router.get("/processing-status/{paper_id}", response_model=ProcessingStatusResponse)
async def get_processing_status(
    paper_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get processing status for a question paper"""
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    paper = db.query(QuestionPaper).filter(QuestionPaper.paper_id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Question paper not found")
    
    return ProcessingStatusResponse(
        paper_id=paper.paper_id,
        status=paper.processing_status.value,
        progress=paper.processing_progress,
        questions_extracted=paper.total_questions_extracted
    )

@router.get("/review-queue", response_model=List[ReviewQueueItem])
async def get_review_queue(
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get questions in review queue"""
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    offset = (page - 1) * limit
    review_items = db.query(ReviewQueue).filter(
        ReviewQueue.status == "PENDING"
    ).offset(offset).limit(limit).all()
    
    return review_items

@router.put("/approve-question/{question_id}")
async def approve_question(
    question_id: int,
    request: QuestionApprovalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Approve or correct a question in review queue"""
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    question = db.query(Question).filter(Question.question_id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    if request.approved:
        # Update question with corrections if provided
        if request.unit_id:
            question.unit_id = request.unit_id
        if request.bloom_level:
            question.bloom_level = request.bloom_level
        if request.marks:
            question.marks = request.marks
        
        # Remove from review queue
        db.query(ReviewQueue).filter(ReviewQueue.question_id == question_id).update({
            "status": "APPROVED"
        })
    else:
        # Mark as rejected
        db.query(ReviewQueue).filter(ReviewQueue.question_id == question_id).update({
            "status": "CORRECTED"
        })
    
    db.commit()
    return {"message": "Question updated successfully"}

@router.get("/analytics/dashboard")
async def get_analytics_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get analytics dashboard data"""
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get basic statistics
    total_papers = db.query(QuestionPaper).count()
    total_questions = db.query(Question).count()
    pending_reviews = db.query(ReviewQueue).filter(ReviewQueue.status == "PENDING").count()
    
    # Get Bloom taxonomy distribution
    bloom_distribution = db.query(Question.bloom_category, db.func.count(Question.question_id)).group_by(Question.bloom_category).all()
    
    # Get course-wise breakdown
    course_breakdown = db.query(QuestionPaper.course_code, db.func.count(QuestionPaper.paper_id)).group_by(QuestionPaper.course_code).all()
    
    return {
        "total_papers": total_papers,
        "total_questions": total_questions,
        "pending_reviews": pending_reviews,
        "bloom_distribution": dict(bloom_distribution),
        "course_breakdown": dict(course_breakdown)
    }

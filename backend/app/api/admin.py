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

class FileUploadResponse(BaseModel):
    upload_id: str
    page_count: int
    file_size: int
    temp_path: str
    file_type: str  # 'pdf' or 'docx'
    original_filename: str

class MetadataSubmitRequest(BaseModel):
    upload_id: str
    course_code: str
    academic_year: int
    semester_type: str
    exam_type: Optional[str] = None  # Optional for syllabus
    exam_date: Optional[datetime] = None
    file_type: Optional[str] = "question_paper"  # 'question_paper' or 'syllabus'

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

def convert_docx_to_pdf(docx_path: str) -> str:
    """Convert DOCX file to PDF (optional - for storage purposes)"""
    try:
        from docx import Document
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        
        doc = Document(docx_path)
        pdf_path = docx_path.replace('.docx', '.pdf').replace('.doc', '.pdf')
        
        c = canvas.Canvas(pdf_path, pagesize=letter)
        y = 750
        for para in doc.paragraphs:
            if para.text.strip():
                # Handle long lines by wrapping
                text = para.text
                words = text.split()
                line = ""
                for word in words:
                    if len(line + word) < 80:
                        line += word + " "
                    else:
                        if line:
                            c.drawString(50, y, line.strip())
                            y -= 20
                        line = word + " "
                        if y < 50:
                            c.showPage()
                            y = 750
                if line:
                    c.drawString(50, y, line.strip())
                    y -= 20
                if y < 50:
                    c.showPage()
                    y = 750
        
        c.save()
        return pdf_path
    except Exception as e:
        # If conversion fails, we can still process DOCX directly
        # Just return the original path and let OCR service handle it
        return docx_path

def get_page_count(file_path: str, file_type: str) -> int:
    """Get page count for PDF or DOCX file. Returns 1 if unable to determine."""
    if file_type == 'pdf':
        try:
            from pdf2image import convert_from_path
            images = convert_from_path(file_path)
            return len(images)
        except ImportError:
            # pdf2image not installed - use fallback
            import sys
            sys.stderr.write("⚠️  pdf2image not available, using fallback page count\n")
            return 1
        except Exception as e:
            # Poppler not installed or other error - use fallback
            import sys
            error_msg = str(e)
            if "poppler" in error_msg.lower() or "path" in error_msg.lower():
                sys.stderr.write(f"⚠️  Poppler not installed: {error_msg}. Using fallback page count.\n")
                sys.stderr.write("   Note: Install poppler for accurate page counts. For now, using default of 1 page.\n")
            else:
                sys.stderr.write(f"⚠️  Error reading PDF: {error_msg}. Using fallback page count.\n")
            sys.stderr.flush()
            return 1  # Return 1 as fallback instead of raising error
    elif file_type == 'docx':
        try:
            from docx import Document
            doc = Document(file_path)
            # Estimate pages based on paragraphs (rough estimate)
            para_count = len([p for p in doc.paragraphs if p.text.strip()])
            # Rough estimate: ~30 paragraphs per page
            return max(1, para_count // 30 + 1)
        except ImportError:
            # python-docx not installed - use fallback
            import sys
            sys.stderr.write("⚠️  python-docx not available, using fallback page count\n")
            return 1
        except Exception as e:
            # Error reading DOCX - use fallback
            import sys
            sys.stderr.write(f"⚠️  Error reading DOCX: {str(e)}. Using fallback page count.\n")
            sys.stderr.flush()
            return 1  # Return 1 as fallback instead of raising error
    else:
        return 1

@router.post("/upload-file", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    file_type: str = Form(...),  # 'question_paper' or 'syllabus'
    current_user: User = Depends(get_current_user)
):
    """Step 1: Upload PDF or DOCX file and return upload details"""
    import sys
    sys.stderr.write(f"📤 Upload request received\n")
    sys.stderr.write(f"   File: {file.filename}\n")
    sys.stderr.write(f"   File type (document): {file_type}\n")
    sys.stderr.write(f"   File type (received): {type(file_type)}, value: '{file_type}'\n")
    sys.stderr.flush()
    
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Validate file_type parameter
    if file_type not in ['question_paper', 'syllabus']:
        error_msg = f"Invalid file_type: '{file_type}'. Must be 'question_paper' or 'syllabus'"
        sys.stderr.write(f"❌ {error_msg}\n")
        sys.stderr.flush()
        raise HTTPException(
            status_code=400, 
            detail=error_msg
        )
    
    filename_lower = file.filename.lower() if file.filename else ""
    if not (filename_lower.endswith('.pdf') or filename_lower.endswith('.docx') or filename_lower.endswith('.doc')):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are allowed")
    
    # Determine file type
    is_docx = filename_lower.endswith('.docx') or filename_lower.endswith('.doc')
    detected_file_type = 'docx' if is_docx else 'pdf'
    
    # Create upload ID and temp directory
    upload_id = f"upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
    temp_dir = "tmp/uploads"
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, upload_id)
    
    # Save file to temp location
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # For DOCX files, we'll keep the original and process it directly
    # No need to convert to PDF for processing (OCR service can handle DOCX)
    
    # Get file size
    file_size = os.path.getsize(temp_path)
    
    # Get page count
    try:
        page_count = get_page_count(temp_path, detected_file_type)
    except HTTPException:
        # Re-raise HTTPExceptions from get_page_count (they already have proper error messages)
        raise
    except Exception as e:
        error_msg = str(e) if str(e) else f"Error processing {detected_file_type.upper()} file"
        sys.stderr.write(f"❌ Error getting page count: {error_msg}\n")
        sys.stderr.write(f"   Exception type: {type(e).__name__}\n")
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        raise HTTPException(status_code=400, detail=error_msg)
    
    return FileUploadResponse(
        upload_id=upload_id,
        page_count=page_count,
        file_size=file_size,
        temp_path=temp_path,
        file_type=detected_file_type,
        original_filename=file.filename or "unknown"
    )

# Keep old endpoint for backward compatibility
@router.post("/upload-pdf", response_model=FileUploadResponse)
async def upload_pdf_legacy(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Legacy endpoint - redirects to upload-file"""
    return await upload_file(file, "question_paper", current_user)

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
    
    # Determine file extension from temp path
    file_ext = '.pdf'  # Default to PDF
    if os.path.exists(temp_path):
        _, ext = os.path.splitext(temp_path)
        if ext:
            file_ext = ext
    
    # Create permanent storage path
    permanent_dir = "storage/papers"
    os.makedirs(permanent_dir, exist_ok=True)
    permanent_path = os.path.join(permanent_dir, f"{request.upload_id}{file_ext}")
    
    # Move file to permanent storage
    shutil.move(temp_path, permanent_path)
    
    # Create database entry
    # For syllabus, exam_type might be None, so we need to handle that
    exam_type_enum = None
    if request.exam_type:
        exam_type_enum = ExamType(request.exam_type)
    elif request.file_type == "question_paper":
        raise HTTPException(status_code=400, detail="Exam type is required for question papers")
    
    paper = QuestionPaper(
        course_code=request.course_code,
        academic_year=request.academic_year,
        semester_type=SemesterType(request.semester_type),
        exam_type=exam_type_enum or ExamType.SEE,  # Default to SEE if not provided (for syllabus)
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
    try:
        if current_user.role != "ADMIN":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Get basic statistics
        total_papers = db.query(QuestionPaper).count()
        total_questions = db.query(Question).count()
        pending_reviews = db.query(ReviewQueue).filter(ReviewQueue.status == "PENDING").count()
        
        # Get Bloom taxonomy distribution (handle empty database)
        try:
            bloom_results = db.query(Question.bloom_category, db.func.count(Question.question_id)).group_by(Question.bloom_category).all()
            bloom_distribution = {str(category or "Unknown"): count for category, count in bloom_results}
        except Exception as e:
            sys.stderr.write(f"⚠️  Error getting bloom distribution: {e}\n")
            bloom_distribution = {}
        
        # Get course-wise breakdown (handle empty database)
        try:
            course_results = db.query(QuestionPaper.course_code, db.func.count(QuestionPaper.paper_id)).group_by(QuestionPaper.course_code).all()
            course_breakdown = {str(code or "Unknown"): count for code, count in course_results}
        except Exception as e:
            sys.stderr.write(f"⚠️  Error getting course breakdown: {e}\n")
            course_breakdown = {}
        
        return {
            "total_papers": total_papers,
            "total_questions": total_questions,
            "pending_reviews": pending_reviews,
            "bloom_distribution": bloom_distribution,
            "course_breakdown": course_breakdown
        }
    except Exception as e:
        import traceback
        import sys
        sys.stderr.write(f"❌ Error in get_analytics_dashboard: {e}\n")
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        raise HTTPException(status_code=500, detail=f"Error fetching dashboard data: {str(e)}")

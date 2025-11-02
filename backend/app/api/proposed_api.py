"""
Proposed API Endpoints - Aligned with Original Proposal
Implements the exact functionality as specified in the original proposal
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.proposed_schema import Semester, Subject, Unit, QPaper, Question
from app.services.ingestion_service import ingestion_service
from app.tasks.proposed_processing import process_question_paper_proposed, create_structured_question_bank
from pydantic import BaseModel
import json

router = APIRouter()

# Pydantic models for API requests/responses
class QuestionSearchRequest(BaseModel):
    subject_name: Optional[str] = None
    semester_name: Optional[str] = None
    unit_name: Optional[str] = None
    keywords: Optional[str] = None
    ai_tag: Optional[str] = None

class QuestionResponse(BaseModel):
    ques_id: int
    ques_text: str
    unit_name: str
    subject_name: str
    semester_name: str
    paper_name: str
    ai_tag: str
    confidence_score: float

class PaperUploadRequest(BaseModel):
    paper_name: str
    file_link: str
    subject_name: str
    semester_name: str

# API Endpoints aligned with proposed system

@router.post("/ingestion/start-monitoring")
async def start_automated_ingestion():
    """
    Start the automated ingestion pipeline
    Integrates with existing Google Drive/GitHub storage to detect and retrieve new question papers
    """
    try:
        # Start monitoring in background
        ingestion_service.start_monitoring()
        return {"message": "Automated ingestion pipeline started successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start ingestion: {str(e)}")

@router.post("/papers/upload")
async def upload_question_paper(request: PaperUploadRequest, db: Session = Depends(get_db)):
    """
    Upload question paper for processing
    Creates QPaper record and triggers processing pipeline
    """
    try:
        # Find or create semester
        semester = db.query(Semester).filter(Semester.sem_name == request.semester_name).first()
        if not semester:
            semester = Semester(sem_name=request.semester_name)
            db.add(semester)
            db.commit()
        
        # Find or create subject
        subject = db.query(Subject).filter(
            Subject.sub_name == request.subject_name,
            Subject.sem_id == semester.sem_id
        ).first()
        if not subject:
            subject = Subject(sub_name=request.subject_name, sem_id=semester.sem_id)
            db.add(subject)
            db.commit()
        
        # Create QPaper record
        qpaper = QPaper(
            paper_name=request.paper_name,
            file_link=request.file_link,
            processing_status="UPLOADED"
        )
        db.add(qpaper)
        db.commit()
        db.refresh(qpaper)
        
        # Trigger processing pipeline
        process_question_paper_proposed.delay(qpaper.paper_id)
        
        return {
            "message": "Question paper uploaded successfully",
            "paper_id": qpaper.paper_id,
            "processing_status": "UPLOADED"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload paper: {str(e)}")

@router.get("/questions/search")
async def search_questions(
    subject_name: Optional[str] = Query(None),
    semester_name: Optional[str] = Query(None),
    unit_name: Optional[str] = Query(None),
    keywords: Optional[str] = Query(None),
    ai_tag: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Search questions in the structured question bank
    Searchable by Subject, Semester, Unit, Paper, and keywords as proposed
    """
    try:
        # Build query based on proposed schema
        query = db.query(Question).join(QPaper).join(Unit).join(Subject).join(Semester)
        
        if subject_name:
            query = query.filter(Subject.sub_name.ilike(f"%{subject_name}%"))
        
        if semester_name:
            query = query.filter(Semester.sem_name.ilike(f"%{semester_name}%"))
        
        if unit_name:
            query = query.filter(Unit.unit_name.ilike(f"%{unit_name}%"))
        
        if keywords:
            query = query.filter(Question.ques_text.ilike(f"%{keywords}%"))
        
        if ai_tag:
            query = query.filter(Question.ai_tag.ilike(f"%{ai_tag}%"))
        
        questions = query.limit(100).all()
        
        # Format response
        results = []
        for question in questions:
            results.append(QuestionResponse(
                ques_id=question.ques_id,
                ques_text=question.ques_text,
                unit_name=question.unit.unit_name if question.unit else "Unclassified",
                subject_name=question.unit.subject.sub_name if question.unit else "Unknown",
                semester_name=question.unit.subject.semester.sem_name if question.unit else "Unknown",
                paper_name=question.paper.paper_name,
                ai_tag=question.ai_tag or "",
                confidence_score=question.confidence_score or 0.0
            ))
        
        return {
            "total_questions": len(results),
            "questions": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/questions/{question_id}")
async def get_question(question_id: int, db: Session = Depends(get_db)):
    """
    Get specific question details
    """
    try:
        question = db.query(Question).filter(Question.ques_id == question_id).first()
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        return QuestionResponse(
            ques_id=question.ques_id,
            ques_text=question.ques_text,
            unit_name=question.unit.unit_name if question.unit else "Unclassified",
            subject_name=question.unit.subject.sub_name if question.unit else "Unknown",
            semester_name=question.unit.subject.semester.sem_name if question.unit else "Unknown",
            paper_name=question.paper.paper_name,
            ai_tag=question.ai_tag or "",
            confidence_score=question.confidence_score or 0.0
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get question: {str(e)}")

@router.get("/subjects")
async def get_subjects(db: Session = Depends(get_db)):
    """
    Get all subjects
    """
    try:
        subjects = db.query(Subject).all()
        return [
            {
                "sub_id": subject.sub_id,
                "sub_name": subject.sub_name,
                "semester_name": subject.semester.sem_name
            }
            for subject in subjects
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get subjects: {str(e)}")

@router.get("/units")
async def get_units(subject_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    """
    Get all units, optionally filtered by subject
    """
    try:
        query = db.query(Unit)
        if subject_id:
            query = query.filter(Unit.sub_id == subject_id)
        
        units = query.all()
        return [
            {
                "unit_id": unit.unit_id,
                "unit_name": unit.unit_name,
                "subject_name": unit.subject.sub_name,
                "semester_name": unit.subject.semester.sem_name
            }
            for unit in units
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get units: {str(e)}")

@router.get("/papers")
async def get_papers(db: Session = Depends(get_db)):
    """
    Get all question papers
    """
    try:
        papers = db.query(QPaper).all()
        return [
            {
                "paper_id": paper.paper_id,
                "paper_name": paper.paper_name,
                "upload_date": paper.upload_date,
                "file_link": paper.file_link,
                "processing_status": paper.processing_status
            }
            for paper in papers
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get papers: {str(e)}")

@router.post("/setup/initialize")
async def initialize_system():
    """
    Initialize the system with proposed structure
    Creates the structured question bank as proposed
    """
    try:
        create_structured_question_bank()
        return {"message": "System initialized successfully with proposed structure"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize system: {str(e)}")

@router.get("/analytics/overview")
async def get_system_overview(db: Session = Depends(get_db)):
    """
    Get system analytics and overview
    """
    try:
        # Count records in each table
        semester_count = db.query(Semester).count()
        subject_count = db.query(Subject).count()
        unit_count = db.query(Unit).count()
        paper_count = db.query(QPaper).count()
        question_count = db.query(Question).count()
        
        # Processing status breakdown
        processing_status = db.query(QPaper.processing_status).group_by(QPaper.processing_status).all()
        status_breakdown = {status[0]: db.query(QPaper).filter(QPaper.processing_status == status[0]).count() 
                           for status in processing_status}
        
        return {
            "system_overview": {
                "semesters": semester_count,
                "subjects": subject_count,
                "units": unit_count,
                "papers": paper_count,
                "questions": question_count
            },
            "processing_status": status_breakdown,
            "message": "System overview generated successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system overview: {str(e)}")

# Export router
__all__ = ["router"]

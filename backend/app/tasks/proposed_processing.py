"""
Proposed Processing Pipeline - Aligned with Original Proposal
Implements the exact processing workflow as specified in the original proposal
"""

from celery import current_task
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.core.config import settings
from app.models.proposed_schema import QPaper, ProposedQuestion, Unit, Subject, Semester
from app.services.enhanced_classification_service import enhanced_classification_service
from app.services.ocr_service import OCRService
from app.core.local_cloud_storage import local_cloud_storage
from app.tasks.celery import celery
import os
import json
from datetime import datetime
from typing import List, Dict
import pymongo
from pymongo import MongoClient

# Database connections
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# MongoDB connection for raw data storage
# MongoDB connection (optional)
mongo_client = None
if settings.MONGODB_URL and settings.MONGODB_URL.strip():
    try:
        mongo_client = MongoClient(settings.MONGODB_URL)
    except Exception as e:
        print(f"⚠️  MongoDB connection failed: {e}. Continuing without MongoDB.")
mongo_db = mongo_client.qpaper_ai if mongo_client else None

# Initialize services
ocr_service = OCRService()

@celery.task(bind=True)
def process_question_paper_proposed(self, paper_id: int):
    """
    Main processing task aligned with proposed system
    Implements the automated pipeline that ingests question papers and generates 
    a structured database of individual questions
    """
    db = SessionLocal()
    
    try:
        # Get paper details
        paper = db.query(QPaper).filter(QPaper.paper_id == paper_id).first()
        if not paper:
            raise Exception(f"Question paper {paper_id} not found")
        
        # Update status to processing
        paper.processing_status = "PROCESSING"
        db.commit()
        
        # Step 1: OCR Processing
        self.update_state(state='PROGRESS', meta={'step': 'OCR', 'progress': 10})
        ocr_results = process_ocr_proposed(paper)
        
        # Step 2: Question Segregation (NLP Model)
        self.update_state(state='PROGRESS', meta={'step': 'Segregation', 'progress': 30})
        questions = segregate_questions_proposed(ocr_results)
        
        # Step 3: AI-Based Mapping (Classification)
        self.update_state(state='PROGRESS', meta={'step': 'Classification', 'progress': 50})
        classified_questions = classify_questions_proposed(questions, paper)
        
        # Step 4: Save to Structured Database
        self.update_state(state='PROGRESS', meta={'step': 'Saving', 'progress': 80})
        save_questions_proposed(classified_questions, paper, db)
        
        # Update paper status
        paper.processing_status = "COMPLETED"
        db.commit()
        
        return {
            'status': 'completed',
            'paper_id': paper_id,
            'questions_extracted': len(classified_questions)
        }
        
    except Exception as e:
        # Update paper status to failed
        paper.processing_status = "FAILED"
        db.commit()
        
        # Log error in MongoDB
        mongo_db.processing_errors.insert_one({
            'paper_id': paper_id,
            'error': str(e),
            'timestamp': datetime.utcnow()
        })
        
        raise e
    finally:
        db.close()

def process_ocr_proposed(paper: QPaper) -> Dict:
    """
    OCR Processing as proposed
    Utilizes OCR to extract text from PDFs/images
    """
    # Create output directory for page images
    output_dir = os.path.join(settings.PAGE_IMAGES_DIR, f"paper_{paper.paper_id}")
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract text from PDF using OCR
    ocr_results = ocr_service.extract_text_from_pdf(paper.file_path, output_dir)
    
    # Upload processed images to cloud storage
    for i, page in enumerate(ocr_results['pages']):
        if page.get('image_path'):
            cloud_key = f"papers/{paper.paper_id}/page_images/page_{i+1}.png"
            cloud_url = local_cloud_storage.upload_file(page['image_path'], cloud_key)
            page['cloud_image_url'] = cloud_url
    
    # Store raw OCR data in MongoDB (as proposed)
    mongo_db.raw_ocr_data.insert_one({
        'paper_id': paper.paper_id,
        'ocr_results': ocr_results,
        'timestamp': datetime.utcnow()
    })
    
    return ocr_results

def segregate_questions_proposed(ocr_results: Dict) -> List[Dict]:
    """
    Question Segregation as proposed
    NLP model automatically segregates the text into distinct, individual questions
    """
    all_questions = []
    
    for page in ocr_results['pages']:
        page_text = page['text']
        
        # Use enhanced classification service for segregation
        questions = enhanced_classification_service.segregate_questions(page_text)
        
        # Add page context to questions
        for question in questions:
            question['page_number'] = page['page_number']
            question['confidence'] = page.get('confidence', 0.0)
            all_questions.append(question)
    
    return all_questions

def classify_questions_proposed(questions: List[Dict], paper: QPaper) -> List[Dict]:
    """
    AI-Based Mapping as proposed
    Machine learning Text Classification model automatically maps each 
    segregated question to the correct Unit within a Subject
    """
    # Load syllabus data from MongoDB
    syllabus = mongo_db.syllabus_documents.find_one({'paper_id': paper.paper_id})
    
    classified_questions = []
    
    for question in questions:
        # Unit classification using AI
        unit_id, unit_confidence = enhanced_classification_service.classify_question_to_unit(
            question['question_text'], syllabus
        )
        question['unit_id'] = unit_id
        question['unit_confidence'] = unit_confidence
        
        # Bloom taxonomy classification
        bloom_level, bloom_category, bloom_confidence = enhanced_classification_service.classify_bloom_taxonomy(
            question['question_text']
        )
        question['bloom_level'] = bloom_level
        question['bloom_category'] = bloom_category
        question['bloom_confidence'] = bloom_confidence
        
        # Generate AI tag as specified in proposed schema
        unit_name = None
        if unit_id and syllabus:
            unit_data = next((u for u in syllabus.get('units', []) if u['unit_id'] == unit_id), None)
            if unit_data:
                unit_name = unit_data['name']
        
        question['ai_tag'] = enhanced_classification_service.generate_ai_tag(
            question['question_text'], unit_name
        )
        
        # Calculate overall confidence
        question['confidence_score'] = (unit_confidence + bloom_confidence) / 2
        
        classified_questions.append(question)
    
    return classified_questions

def save_questions_proposed(questions: List[Dict], paper: QPaper, db):
    """
    Save to Structured Question Bank as proposed
    Creates a relational database where every question is a distinct record
    """
    for question_data in questions:
        # Create Question record as specified in proposed schema
        question = ProposedQuestion(
            ques_text=question_data['question_text'],
            unit_id=question_data.get('unit_id'),
            paper_id=paper.paper_id,
            ai_tag=question_data.get('ai_tag'),
            confidence_score=question_data.get('confidence_score')
        )
        
        db.add(question)
    
    db.commit()
    
    # Store additional metadata in MongoDB
    mongo_db.question_embeddings.insert_one({
        'paper_id': paper.paper_id,
        'questions': questions,
        'processing_metadata': {
            'total_questions': len(questions),
            'avg_confidence': sum(q.get('confidence_score', 0) for q in questions) / len(questions),
            'processing_timestamp': datetime.utcnow()
        }
    })

def create_structured_question_bank():
    """
    Create the final output as proposed
    A relational database where every question is a distinct record, 
    searchable by Subject, Semester, Unit, Paper, and keywords
    """
    db = SessionLocal()
    
    try:
        # Create sample data structure as proposed
        # SEMESTER table
        semester = Semester(sem_name="Semester 1")
        db.add(semester)
        db.commit()
        
        # SUBJECT table
        subject = Subject(sub_name="Database Management Systems", sem_id=semester.sem_id)
        db.add(subject)
        db.commit()
        
        # UNIT table
        unit = Unit(unit_name="Introduction to Databases", sub_id=subject.sub_id)
        db.add(unit)
        db.commit()
        
        # QPAPER table
        qpaper = QPaper(
            paper_name="DBMS Midterm 2024",
            file_link="https://drive.google.com/sample.pdf",
            processing_status="COMPLETED"
        )
        db.add(qpaper)
        db.commit()
        
        # QUESTION table (Central table as proposed)
        question = ProposedQuestion(
            ques_text="What is a database management system?",
            unit_id=unit.unit_id,
            paper_id=qpaper.paper_id,
            ai_tag="Unit:Introduction to Databases|Bloom:Remembering|HighConfidence"
        )
        db.add(question)
        db.commit()
        
        print("✅ Structured Question Bank created successfully")
        print(f"   - Semester: {semester.sem_name}")
        print(f"   - Subject: {subject.sub_name}")
        print(f"   - Unit: {unit.unit_name}")
        print(f"   - Paper: {qpaper.paper_name}")
        print(f"   - Question: {question.ques_text[:50]}...")
        
    except Exception as e:
        print(f"❌ Error creating structured question bank: {e}")
        db.rollback()
    finally:
        db.close()

# Export functions for use in other modules
__all__ = [
    "process_question_paper_proposed",
    "create_structured_question_bank"
]

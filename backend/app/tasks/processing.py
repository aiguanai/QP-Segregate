from celery import current_task
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.core.config import settings
from app.models.question_paper import QuestionPaper, ProcessingStatus
from app.models.question import Question, ReviewQueue, BloomLevel, BloomCategory, DifficultyLevel
from app.models.course import CourseUnit
from app.services.ocr_service import OCRService
from app.services.classification_service import ClassificationService
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

# MongoDB connection
mongo_client = MongoClient(settings.MONGODB_URL)
mongo_db = mongo_client.qpaper_ai

# Initialize services
ocr_service = OCRService()
classification_service = ClassificationService()

@celery.task(bind=True)
def process_question_paper(self, paper_id: int):
    """Main task to process a question paper"""
    db = SessionLocal()
    
    try:
        # Get paper details
        paper = db.query(QuestionPaper).filter(QuestionPaper.paper_id == paper_id).first()
        if not paper:
            raise Exception(f"Question paper {paper_id} not found")
        
        # Update status to processing
        paper.processing_status = ProcessingStatus.PROCESSING
        paper.processing_progress = 0
        db.commit()
        
        # Step 1: OCR Processing
        self.update_state(state='PROGRESS', meta={'step': 'OCR', 'progress': 10})
        ocr_results = process_ocr(paper)
        
        # Step 2: Question Parsing
        self.update_state(state='PROGRESS', meta={'step': 'Parsing', 'progress': 30})
        questions = parse_questions(ocr_results)
        
        # Step 3: Classification
        self.update_state(state='PROGRESS', meta={'step': 'Classification', 'progress': 50})
        classified_questions = classify_questions(questions, paper.course_code)
        
        # Step 4: Duplicate Detection
        self.update_state(state='PROGRESS', meta={'step': 'Deduplication', 'progress': 70})
        deduplicated_questions = detect_duplicates(classified_questions, paper.course_code)
        
        # Step 5: Save to Database
        self.update_state(state='PROGRESS', meta={'step': 'Saving', 'progress': 90})
        save_questions(deduplicated_questions, paper, db)
        
        # Update paper status
        paper.processing_status = ProcessingStatus.COMPLETED
        paper.processing_progress = 100
        paper.total_questions_extracted = len(deduplicated_questions)
        db.commit()
        
        return {
            'status': 'completed',
            'paper_id': paper_id,
            'questions_extracted': len(deduplicated_questions)
        }
        
    except Exception as e:
        # Update paper status to failed
        paper.processing_status = ProcessingStatus.FAILED
        db.commit()
        
        # Log error to MongoDB
        mongo_db.processing_errors.insert_one({
            'paper_id': paper_id,
            'error': str(e),
            'timestamp': datetime.utcnow(),
            'task_id': self.request.id
        })
        
        raise e
    finally:
        db.close()

def process_ocr(paper: QuestionPaper) -> Dict:
    """Process PDF with OCR using local cloud storage"""
    # Create output directory for page images
    output_dir = os.path.join(settings.PAGE_IMAGES_DIR, f"paper_{paper.paper_id}")
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract text from PDF
    ocr_results = ocr_service.extract_text_from_pdf(paper.pdf_path, output_dir)
    
    # Upload processed images to local cloud storage
    for i, page in enumerate(ocr_results['pages']):
        if page.get('image_path'):
            cloud_key = f"papers/{paper.paper_id}/page_images/page_{i+1}.png"
            cloud_url = local_cloud_storage.upload_file(page['image_path'], cloud_key)
            page['cloud_image_url'] = cloud_url
            # Keep local path for now, will be cleaned up later
            page['local_image_path'] = page['image_path']
    
    # Store raw OCR data in MongoDB
    mongo_db.raw_ocr_data.insert_one({
        'paper_id': paper.paper_id,
        'course_code': paper.course_code,
        'ocr_results': ocr_results,
        'timestamp': datetime.utcnow()
    })
    
    return ocr_results

def parse_questions(ocr_results: Dict) -> List[Dict]:
    """Parse questions from OCR text"""
    all_questions = []
    
    for page in ocr_results['pages']:
        if page['confidence'] > 40:  # Only process pages with decent OCR confidence
            questions = ocr_service.extract_questions_from_text(page['text'])
            
            for question in questions:
                question['page_number'] = page['page_number']
                question['ocr_confidence'] = page['confidence']
                all_questions.append(question)
    
    return all_questions

def classify_questions(questions: List[Dict], course_code: str) -> List[Dict]:
    """Classify questions for unit, Bloom level, and difficulty"""
    # Load syllabus data from MongoDB
    syllabus = mongo_db.syllabus_documents.find_one({'course_code': course_code})
    
    classified_questions = []
    
    for question in questions:
        # Unit classification
        unit_id, unit_confidence = classification_service.classify_unit(
            question['question_text'], course_code, syllabus
        )
        question['unit_id'] = unit_id
        question['unit_confidence'] = unit_confidence
        
        # Bloom taxonomy classification
        bloom_level, bloom_category, bloom_confidence = classification_service.classify_bloom_taxonomy(
            question['question_text']
        )
        question['bloom_level'] = bloom_level
        question['bloom_category'] = bloom_category
        question['bloom_confidence'] = bloom_confidence
        
        # Difficulty estimation
        difficulty = classification_service.estimate_difficulty(question)
        question['difficulty_level'] = difficulty
        
        # Extract features
        features = classification_service.extract_question_features(question['question_text'])
        question.update(features)
        
        # Generate embedding
        embedding = classification_service.generate_embedding(question['question_text'])
        question['embedding'] = embedding.tolist()
        
        classified_questions.append(question)
    
    return classified_questions

def detect_duplicates(questions: List[Dict], course_code: str) -> List[Dict]:
    """Detect and group similar questions"""
    # Get existing embeddings for the course
    existing_embeddings = []
    existing_question_ids = []
    
    # Query existing questions for the course
    db = SessionLocal()
    existing_questions = db.query(Question).filter(Question.course_code == course_code).all()
    
    for eq in existing_questions:
        # Get embedding from vector database (Pinecone/Qdrant)
        # For now, we'll skip this and treat all as new
        pass
    
    deduplicated = []
    
    for question in questions:
        # Find similar questions
        similar_questions = classification_service.find_similar_questions(
            question['question_text'], course_code, existing_embeddings
        )
        
        if similar_questions:
            # Group with existing question
            parent_id = similar_questions[0][0]  # Most similar question ID
            question['is_canonical'] = False
            question['parent_question_id'] = parent_id
            question['similarity_score'] = similar_questions[0][1]
        else:
            # New canonical question
            question['is_canonical'] = True
            question['parent_question_id'] = None
            question['similarity_score'] = None
        
        deduplicated.append(question)
    
    db.close()
    return deduplicated

def save_questions(questions: List[Dict], paper: QuestionPaper, db):
    """Save questions to database"""
    review_count = 0
    
    for question_data in questions:
        # Create question object
        question = Question(
            paper_id=paper.paper_id,
            course_code=paper.course_code,
            unit_id=question_data.get('unit_id'),
            question_number=question_data['question_number'],
            question_text=question_data['question_text'],
            marks=question_data.get('marks'),
            bloom_level=BloomLevel(question_data['bloom_level']) if question_data.get('bloom_level') else None,
            bloom_category=BloomCategory(question_data['bloom_category']) if question_data.get('bloom_category') else None,
            bloom_confidence=question_data.get('bloom_confidence'),
            difficulty_level=DifficultyLevel(question_data['difficulty_level']),
            classification_confidence=question_data.get('unit_confidence', 0),
            is_canonical=question_data.get('is_canonical', True),
            parent_question_id=question_data.get('parent_question_id'),
            similarity_score=question_data.get('similarity_score'),
            has_subparts=question_data.get('has_subparts', False),
            has_mathematical_notation=question_data.get('has_mathematical_notation', False),
            page_number=question_data.get('page_number')
        )
        
        db.add(question)
        db.flush()  # Get the question_id
        
        # Add to review queue if confidence is low
        if (question_data.get('unit_confidence', 0) < 0.7 or 
            question_data.get('bloom_confidence', 0) < 0.7):
            
            review_queue = ReviewQueue(
                question_id=question.question_id,
                issue_type='LOW_CONFIDENCE',
                suggested_correction=json.dumps({
                    'unit_id': question_data.get('unit_id'),
                    'bloom_level': question_data.get('bloom_level'),
                    'marks': question_data.get('marks')
                }),
                priority=2
            )
            
            db.add(review_queue)
            review_count += 1
        
        # Store embedding in vector database
        if 'embedding' in question_data:
            # Store in Pinecone/Qdrant
            # For now, store in MongoDB
            mongo_db.question_embeddings.insert_one({
                'question_id': question.question_id,
                'course_code': paper.course_code,
                'embedding': question_data['embedding'],
                'metadata': {
                    'unit_id': question_data.get('unit_id'),
                    'marks': question_data.get('marks'),
                    'bloom_level': question_data.get('bloom_level')
                }
            })
    
    # Update paper with review count
    paper.questions_in_review = review_count
    db.commit()

@celery.task
def cleanup_temp_uploads():
    """Clean up expired temporary uploads"""
    import time
    
    temp_dir = settings.TEMP_UPLOAD_DIR
    current_time = time.time()
    expire_time = settings.TEMP_UPLOAD_EXPIRE_HOURS * 3600
    
    if os.path.exists(temp_dir):
        for filename in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, filename)
            if os.path.isfile(file_path):
                file_age = current_time - os.path.getmtime(file_path)
                if file_age > expire_time:
                    os.remove(file_path)
                    print(f"Removed expired temp file: {filename}")
    
    return {"cleaned_files": "temp_uploads_cleaned"}

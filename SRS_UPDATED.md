# Software Requirement Specification (SRS) - QPaper AI
## Updated to Match Actual Implementation

---

## 1. Hardware Requirements

The system has two main components: the Processing Server (where OCR/AI runs) and the Client Devices (for user access).

| Component | Minimum Specification | Purpose |
|-----------|----------------------|---------|
| **Processing Server** | | |
| CPU | Quad-Core CPU (2.5 GHz or higher) | Running the ingestion pipeline, database, and web server. |
| RAM | 16 GB RAM | Required for holding large files, running AI models (especially NLP), and database caching. |
| Storage | 500 GB SSD Storage | Fast I/O for quick reading of question papers and database operations. |
| GPU | GPU (Optional but Recommended) | A dedicated NVIDIA GPU (4GB VRAM) is highly recommended for faster training and inference of the deep learning NLP classification model. |
| **Client Device** | | |
| Browser | Modern Browser Support (Chrome, Firefox, Edge) | Accessing the web-based search and admin interface. |
| Hardware | Standard Laptop/Desktop (8GB RAM) | Standard usage requirements. |

### Docker Deployment Requirements
- **Docker Engine**: 20.10+
- **Docker Compose**: 2.0+
- **Container Resources**: Minimum 4GB RAM allocated for containers

---

## 2. Software Requirements

These requirements specify the operating environment and the core tools needed for development and deployment.

| Category | Requirement | Purpose |
|----------|-------------|---------|
| **Operating System** | Linux (Ubuntu/Debian) or Windows/macOS | Development and Deployment Environment. Linux is preferred for server and containerization. |
| **Programming Language** | Python 3.11+ | Core language for the AI/ML pipeline, system integration, and backend development. |
| **Backend Web Framework** | FastAPI with Uvicorn | Modern async web framework for building REST APIs with automatic OpenAPI documentation. Provides high performance and async capabilities. |
| **Frontend Framework** | Next.js (React) with TypeScript | Building the responsive web-based user interface for search and admin operations. |
| **Frontend Styling** | Tailwind CSS | Utility-first CSS framework for rapid UI development. |
| **Task Queue System** | Celery with Redis | Background task processing for OCR and AI classification operations. Celery handles async tasks, Redis provides the message broker. |
| **Database Management** | PostgreSQL 15+ (RDBMS) | Storing structured question data and metadata, ensuring ACID properties. |
| **Database Management** | MongoDB 6+ (NoSQL) | Storing raw OCR outputs, AI logs, and flexible, unstructured data. |
| **Cache & Queue** | Redis 7+ | In-memory database for task queuing, caching, and session management. |
| **AI/ML Libraries** | scikit-learn, PyTorch, sentence-transformers, transformers (Hugging Face), NLTK, SpaCy | Developing and deploying the NLP Text Classification and Segmentation models. |
| **OCR Tool** | Tesseract OCR Engine (Primary) | Converting image/PDF text into digital text. OpenCV used for image preprocessing. |
| **OCR Enhancement** | Google Cloud Vision API (Optional) | Optional cloud-based OCR for improved accuracy on complex documents. |
| **Image Processing** | OpenCV, Pillow | Image preprocessing, enhancement, and format conversion for improved OCR accuracy. |
| **File Storage** | AWS S3 or Google Cloud Storage | Cloud-based file storage for question papers and processed images. Local storage as fallback option. |
| **Containerization** | Docker & Docker Compose | Containerization for consistent deployment across environments. Essential for managing multiple services. |
| **Version Control** | Git and GitHub/GitLab | Managing source code and project collaboration. |

### Additional Backend Libraries
- **SQLAlchemy**: ORM for database operations
- **Pydantic**: Data validation and settings management
- **PyMongo**: MongoDB driver
- **PyTesseract**: Python wrapper for Tesseract OCR
- **pdf2image**: PDF to image conversion
- **python-jose**: JWT authentication
- **passlib**: Password hashing

---

## 3. Functional Requirements

These define the specific functions the system must perform to meet the user's needs.

### 3.1 Question Paper Ingestion and Processing

The system shall allow an authorized administrator to initiate the ingestion process for new question papers.

**FR-1.1 File Retrieval:** The system must connect to the configured Google Drive/GitHub repository and retrieve the target PDF or image file based on its pre-defined Subject/Semester location.

**Implementation:** 
- Automated ingestion service (`ingestion_service.py`)
- Google Drive API integration
- GitHub repository monitoring
- Background task processing via Celery

**FR-1.2 OCR Execution:** The system shall apply OCR to the retrieved file, generating a raw text output for the entire paper.

**Implementation:**
- Tesseract OCR engine with OpenCV preprocessing
- PDF to image conversion
- Page-by-page text extraction
- Confidence scoring per page

**FR-1.3 Segmentation:** The system shall use an NLP model to accurately parse the raw text output, segregating it into distinct individual question records, including question number and text.

**Implementation:**
- Enhanced NLP classification service
- Pattern-based question detection
- Question number extraction
- Text cleaning and normalization

---

### 3.2 AI-Driven Curriculum Mapping and Classification

The system must automatically classify and structure each segregated question.

**FR-2.1 Unit Mapping:** The system shall apply the trained Text Classification model to each question text to predict the corresponding Unit ID within the known Subject.

**Implementation:**
- TF-IDF vectorization with cosine similarity
- Machine learning classification model
- Confidence score calculation
- Syllabus-based unit matching

**FR-2.2 Database Insertion:** The system must insert the structured data (Question Text, Predicted Unit ID, Source Paper ID) into the PostgreSQL RDBMS, ensuring all foreign key constraints are satisfied.

**Implementation:**
- SQLAlchemy ORM for database operations
- Transaction management
- Foreign key relationships (Semester → Subject → Unit → Question)
- Data validation before insertion

**FR-2.3 Status Logging:** The system shall record the raw OCR text and the AI model's confidence scores into the MongoDB NoSQL database, linked by an RDBMS reference ID.

**Implementation:**
- MongoDB collections for raw data
- RDBMS-MongoDB reference linking
- Processing metadata storage
- Error logging and debugging information

---

### 3.3 Comprehensive Search and Retrieval Interface

The system must provide a user-friendly web interface for searching and retrieving questions.

**FR-3.1 Structured Search:** Users must be able to filter questions using combinations of RDBMS metadata: Semester, Subject, and Unit.

**Implementation:**
- RESTful API endpoints (`/api/proposed/questions/search`)
- Query building with SQLAlchemy
- Multi-field filtering
- Efficient database queries with proper indexing

**FR-3.2 Keyword Search:** Users must be able to perform a full-text search across all stored question texts.

**Implementation:**
- PostgreSQL full-text search
- SQL LIKE queries for keyword matching
- Case-insensitive search
- Pagination support

**FR-3.3 Question Display:** The system shall display the retrieved questions along with their associated metadata (Source Paper Name, Unit Name, and Upload Date).

**Implementation:**
- Structured API responses
- JSON format with all metadata
- Frontend rendering in Next.js
- Responsive UI design

---

### 3.4 Administrative Review and Correction

The system must allow authorized administrators to review and correct the AI's predictions to maintain data accuracy.

**FR-4.1 Mapping Review:** An administrator must be able to view all newly processed questions and override the AI's predicted Unit ID with a manually selected correct Unit ID.

**Implementation:**
- Review queue system (`review_queue` table)
- Admin API endpoints (`/api/admin/approve-question`)
- Confidence-based filtering
- Manual unit assignment

**FR-4.2 Text Correction:** An administrator must be able to edit the stored Question Text to fix any errors introduced by the OCR or segmentation process.

**Implementation:**
- Question update endpoints
- Text editing interface
- Validation before saving
- Change tracking

**FR-4.3 Paper Management:** An administrator must be able to mark a processed paper as "Approved" or "Awaiting Review" and manage the source paper records.

**Implementation:**
- Processing status tracking (`UPLOADED`, `PROCESSING`, `COMPLETED`, `FAILED`, `APPROVED`)
- Paper management endpoints
- Status update workflow
- Bulk operations support

---

## 4. Non-Functional Requirements

### 4.1 Performance Requirements
- **OCR Processing**: Process 10-page PDF in under 2 minutes
- **Question Classification**: Classify 50 questions in under 30 seconds
- **Search Response**: Return search results within 500ms
- **API Response Time**: Average API response time under 200ms

### 4.2 Scalability Requirements
- Support concurrent processing of multiple papers
- Horizontal scaling of Celery workers
- Database connection pooling
- Caching frequently accessed data

### 4.3 Security Requirements
- JWT-based authentication
- Role-based access control (Admin/Student)
- Secure password hashing (bcrypt)
- Environment variable management for secrets
- Input validation and sanitization

### 4.4 Reliability Requirements
- Database transaction integrity
- Error logging and monitoring
- Automatic retry for failed tasks
- Health check endpoints
- Graceful error handling

### 4.5 Deployment Requirements
- Docker containerization for all services
- Environment-based configuration
- Cloud-ready deployment
- Database migration support
- Backup and recovery procedures

---

## 5. System Architecture

### 5.1 Technology Stack Summary

**Backend:**
- FastAPI (Web Framework)
- PostgreSQL (Primary Database)
- MongoDB (Document Database)
- Redis (Cache & Queue)
- Celery (Task Queue)

**Frontend:**
- Next.js (React Framework)
- TypeScript
- Tailwind CSS

**AI/ML:**
- Tesseract OCR
- spaCy (NLP)
- scikit-learn (ML)
- PyTorch (Deep Learning)
- Transformers (Hugging Face)

**Deployment:**
- Docker & Docker Compose
- AWS S3 / Google Cloud Storage

---

## 6. API Specifications

The system provides RESTful API endpoints organized into modules:

### Authentication Module
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `GET /api/auth/me` - Get current user

### Proposed System Module (Aligned with Original Proposal)
- `POST /api/proposed/ingestion/start-monitoring` - Start automated ingestion
- `POST /api/proposed/papers/upload` - Upload question paper
- `GET /api/proposed/questions/search` - Search questions
- `GET /api/proposed/subjects` - Get all subjects
- `GET /api/proposed/units` - Get all units
- `POST /api/proposed/setup/initialize` - Initialize system

### Admin Module
- `POST /api/admin/upload-pdf` - Upload PDF file
- `GET /api/admin/review-queue` - Get review queue
- `PUT /api/admin/approve-question/{question_id}` - Approve question

### Student Module
- `GET /api/student/search` - Search questions
- `POST /api/student/bookmark/{question_id}` - Bookmark question

---

## 7. Database Schema (As Proposed)

### Relational Structure (PostgreSQL)
- **SEMESTER** (sem_id, sem_name)
- **SUBJECT** (sub_id, sub_name, sem_id)
- **UNIT** (unit_id, unit_name, sub_id)
- **QPAPER** (paper_id, paper_name, upload_date, file_link)
- **QUESTION** (ques_id, ques_text, unit_id, paper_id, ai_tag)

### Document Structure (MongoDB)
- **raw_ocr_data** - Raw OCR processing results
- **syllabus_documents** - Course syllabus data
- **question_embeddings** - Vector embeddings metadata
- **processing_errors** - Error logs

---

## 8. Deployment Architecture

### Development Environment
```bash
docker-compose up
```

### Production Environment
```bash
docker-compose -f docker-compose.cloud.yml up
```

### Service Dependencies
1. PostgreSQL (Database)
2. MongoDB (Document Store)
3. Redis (Cache/Queue)
4. Backend API (FastAPI)
5. Celery Worker (Background Tasks)
6. Celery Beat (Scheduled Tasks)
7. Frontend (Next.js)

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 2.0 | Current | Updated to match actual implementation: FastAPI, Python 3.11+, Redis, Celery, Next.js |
| 1.0 | Original | Initial SRS with Django/Flask, Python 3.8+ |

---

**Document Status:** ✅ **Aligned with Implementation**


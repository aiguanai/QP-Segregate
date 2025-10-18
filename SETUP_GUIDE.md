# QPaper AI - Setup Guide

This guide will help you set up and run the QPaper AI system on your local machine.

## Prerequisites

- **Docker & Docker Compose** (Recommended for full setup)
- **Python 3.11+** (for development)
- **Node.js 18+** (for frontend development)
- **PostgreSQL 15+** (if not using Docker)
- **MongoDB 6+** (if not using Docker)
- **Redis 7+** (if not using Docker)

## Quick Start (Docker)

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd QPseg
   ```

2. **Run Setup Script**
   ```bash
   # On Windows
   setup.bat
   
   # On Linux/Mac
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Configure Environment**
   - Edit `backend/.env` with your database credentials and API keys
   - Update `frontend/.env.local` if needed

4. **Start Services**
   ```bash
   docker-compose up
   ```

5. **Access Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Development Setup

### Backend Development

1. **Setup Python Environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Download spaCy Model**
   ```bash
   python -m spacy download en_core_web_sm
   ```

3. **Configure Database**
   - Update `backend/.env` with your database URLs
   - Ensure PostgreSQL, MongoDB, and Redis are running

4. **Run Backend**
   ```bash
   uvicorn app.main:app --reload
   ```

5. **Run Celery Worker** (in separate terminal)
   ```bash
   celery -A app.tasks.celery worker --loglevel=info
   ```

### Frontend Development

1. **Install Dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Run Frontend**
   ```bash
   npm run dev
   ```

## Environment Configuration

### Backend (.env)

```env
# Database Configuration
DATABASE_URL=postgresql://qpaper_user:qpaper_password@localhost:5432/qpaper_ai
MONGODB_URL=mongodb://qpaper_user:qpaper_password@localhost:27017/qpaper_ai?authSource=admin
REDIS_URL=redis://localhost:6379

# JWT Configuration
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# External APIs (Optional)
PINECONE_API_KEY=your-pinecone-api-key
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_S3_BUCKET=your-s3-bucket-name
MATHPIX_API_KEY=your-mathpix-api-key
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Database Setup

### PostgreSQL Tables

The system automatically creates the following tables:

- **users** - User accounts (admin/student)
- **courses** - Course information
- **course_offerings** - Course-branch-year mappings
- **course_equivalence** - Equivalent courses
- **course_units** - Course units and topics
- **question_papers** - Uploaded question papers
- **questions** - Extracted questions
- **review_queue** - Questions pending review
- **student_bookmarks** - Student bookmarks

### MongoDB Collections

- **raw_ocr_data** - OCR processing results
- **syllabus_documents** - Course syllabus data
- **question_embeddings** - Question embeddings metadata
- **processing_errors** - Error logs
- **temp_uploads** - Temporary upload tracking

## Initial Data Setup

### 1. Create Admin User

```python
# Run this in Python shell or create a script
from app.core.database import SessionLocal
from app.models.user import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

db = SessionLocal()
admin_user = User(
    username="admin",
    email="admin@qpaper.ai",
    password_hash=pwd_context.hash("admin123"),
    role="ADMIN"
)
db.add(admin_user)
db.commit()
```

### 2. Add Sample Courses

```python
from app.models.course import Course, CourseUnit

# Add sample courses
courses = [
    Course(course_code="CS301", course_name="Database Management Systems", credits=4, course_type="CORE"),
    Course(course_code="CS302", course_name="Computer Networks", credits=4, course_type="CORE"),
    Course(course_code="MA201", course_name="Mathematics", credits=3, course_type="CORE"),
]

for course in courses:
    db.add(course)

# Add course units
units = [
    CourseUnit(course_code="CS301", unit_number=1, unit_name="Introduction to Databases", topics="DBMS concepts, data models"),
    CourseUnit(course_code="CS301", unit_number=2, unit_name="SQL and Relational Algebra", topics="SQL queries, joins, normalization"),
    CourseUnit(course_code="CS301", unit_number=3, unit_name="Database Design", topics="ER modeling, normalization forms"),
]

for unit in units:
    db.add(unit)

db.commit()
```

## Usage Guide

### Admin Workflow

1. **Login** as admin at http://localhost:3000/admin/login
2. **Upload Question Paper**:
   - Go to Upload section
   - Upload PDF file
   - Fill metadata form (course, year, semester, exam type)
   - Submit for processing
3. **Review Queue**:
   - Check questions with low confidence
   - Approve or correct classifications
4. **Analytics**:
   - View processing statistics
   - Monitor system performance

### Student Workflow

1. **Login** as student at http://localhost:3000/student/login
2. **Search Questions**:
   - Use semantic search
   - Apply filters (course, unit, marks, Bloom level)
   - View question variants
3. **Practice Mode**:
   - Generate random questions
   - Practice with different difficulty levels
4. **Bookmarks**:
   - Save important questions
   - Add personal notes

## API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `GET /api/auth/me` - Get current user

### Admin Endpoints
- `POST /api/admin/upload-pdf` - Upload PDF file
- `POST /api/admin/submit-metadata` - Submit paper metadata
- `GET /api/admin/processing-status/{paper_id}` - Get processing status
- `GET /api/admin/review-queue` - Get review queue
- `PUT /api/admin/approve-question/{question_id}` - Approve question
- `GET /api/admin/analytics/dashboard` - Get analytics

### Student Endpoints
- `GET /api/student/my-courses` - Get student courses
- `POST /api/student/search` - Search questions
- `GET /api/student/question/{question_id}/variants` - Get question variants
- `POST /api/student/bookmark/{question_id}` - Bookmark question
- `GET /api/student/bookmarks` - Get bookmarks
- `POST /api/student/random-questions` - Get random questions

### Course Endpoints
- `GET /api/courses` - Get courses
- `GET /api/courses/{course_code}` - Get specific course
- `GET /api/courses/{course_code}/units` - Get course units

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check database URLs in `.env`
   - Ensure databases are running
   - Verify credentials

2. **OCR Processing Fails**
   - Install Tesseract OCR
   - Check PDF file format
   - Verify image quality

3. **Celery Tasks Not Running**
   - Check Redis connection
   - Ensure Celery worker is running
   - Check task logs

4. **Frontend Build Errors**
   - Clear node_modules and reinstall
   - Check Node.js version
   - Update dependencies

### Logs

- **Backend logs**: Check console output
- **Celery logs**: Check worker output
- **Processing errors**: Check MongoDB `processing_errors` collection

## Production Deployment

### Docker Production

1. **Update docker-compose.yml** for production
2. **Set environment variables** for production
3. **Configure reverse proxy** (nginx)
4. **Set up SSL certificates**
5. **Configure monitoring** and logging

### Environment Variables for Production

```env
# Security
JWT_SECRET_KEY=strong-random-secret-key
DATABASE_URL=postgresql://user:pass@prod-db:5432/qpaper_ai
MONGODB_URL=mongodb://user:pass@prod-mongo:27017/qpaper_ai

# External Services
PINECONE_API_KEY=your-production-pinecone-key
AWS_ACCESS_KEY_ID=your-production-aws-key
AWS_SECRET_ACCESS_KEY=your-production-aws-secret
```

## Support

For issues and questions:
1. Check this documentation
2. Review error logs
3. Check GitHub issues
4. Contact the development team

## License

This project is licensed under the MIT License - see the LICENSE file for details.

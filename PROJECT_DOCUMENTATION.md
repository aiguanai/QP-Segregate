# QPaper AI - Automated Question Paper Management System
## Database Management Systems Project Documentation

---

## 1. Introduction

### 1.1 Objective

The primary objective of this project is to develop an intelligent **Question Paper Management System (QP-Segregate)** that automates the extraction, classification, and organization of university question papers. The system aims to:

- **Automate Question Extraction**: Utilize LLM (Large Language Model) APIs to automatically extract questions, marks, and Bloom's taxonomy levels from uploaded PDF/DOCX question papers, eliminating manual data entry.

- **Intelligent Classification**: Implement AI-powered classification to categorize questions into appropriate course units and associate them with relevant topics from the syllabus, ensuring accurate organization.

- **Review Workflow Management**: Provide administrators with a comprehensive review queue system to validate, edit, and approve AI-generated classifications before making questions available to students.

- **Student-Centric Interface**: Enable students to search, filter, bookmark, and practice questions with advanced filtering capabilities including course selection, unit-based filtering, marks range, Bloom's taxonomy levels, and review status.

- **Duplicate Detection**: Prevent duplicate question paper uploads by checking course code, exam type, and exam date combinations, maintaining data integrity.

- **Image Handling**: Support extraction and display of diagrams, tables, and images associated with questions, enhancing the learning experience.

- **Scalable Architecture**: Design a robust system using PostgreSQL for structured data, MongoDB for unstructured content, and Redis for caching, ensuring high performance and scalability.

### 1.2 Scope

This project encompasses the development of a full-stack web application for managing question papers in an educational institution. The scope includes:

- **Admin Module**: Complete administrative interface for uploading question papers, managing courses and units, reviewing AI-classified questions, editing question metadata, uploading question images, and maintaining the question bank.

- **Student Module**: Comprehensive student interface featuring course selection, advanced search with multiple filters, bookmark functionality, practice mode, and access to original question paper files.

- **AI Processing Pipeline**: Integration with OpenAI API for question extraction and classification, including handling of subparts (e.g., 2.a, 2.b) as separate question records.

- **Database Design**: Normalized relational database schema supporting courses, units, questions, users, bookmarks, review queues, and activity logging.

- **Authentication & Authorization**: Role-based access control with separate admin and student authentication, including OAuth integration for student login.

The system is designed to handle multiple courses, academic years, semesters, and exam types (CIE 1, CIE 2, Improvement CIE, SEE), making it suitable for comprehensive question paper management across an entire academic institution.

---

## 2. Software Requirement Specification

### 2.1 Software Requirements

#### Backend Technologies
- **Python 3.9+**: Core programming language for backend development
- **FastAPI 0.104+**: Modern, fast web framework for building REST APIs with automatic OpenAPI documentation
- **SQLAlchemy 2.0+**: Python SQL toolkit and Object-Relational Mapping (ORM) library for database interactions
- **PostgreSQL 14+**: Primary relational database for structured data storage (courses, users, questions, papers)
- **MongoDB 6.0+**: NoSQL database for storing unstructured OCR results and embeddings
- **Redis 7.0+**: In-memory data structure store for caching and session management
- **OpenAI API**: Integration with GPT-4 for question extraction and classification
- **PyPDF2/pdfplumber**: PDF text extraction libraries
- **python-docx**: DOCX file processing library
- **Pillow**: Image processing library for handling question diagrams
- **Pydantic**: Data validation using Python type annotations
- **Uvicorn**: ASGI server for running FastAPI applications

#### Frontend Technologies
- **Node.js 18+**: JavaScript runtime environment
- **Next.js 13+**: React framework for production with server-side rendering
- **React 18+**: JavaScript library for building user interfaces
- **TypeScript**: Typed superset of JavaScript for type safety
- **Tailwind CSS 3+**: Utility-first CSS framework for rapid UI development
- **Axios**: Promise-based HTTP client for API requests
- **React Hot Toast**: Toast notification library for user feedback
- **Heroicons**: Icon library for UI components
- **@react-oauth/google**: Google OAuth integration for student authentication

#### Development Tools
- **Docker & Docker Compose**: Containerization for consistent development and deployment
- **Git**: Version control system
- **Postman/Thunder Client**: API testing tools
- **VS Code**: Integrated development environment

#### Cloud Services (Optional)
- **Supabase**: Cloud-hosted PostgreSQL database
- **MongoDB Atlas**: Cloud-hosted MongoDB
- **Redis Cloud/Upstash**: Cloud-hosted Redis
- **AWS S3**: Object storage for question paper files (optional)

### 2.2 Hardware Requirements

#### Minimum System Requirements
- **Processor**: Intel Core i5 or AMD equivalent (2.0 GHz or higher)
- **RAM**: 8 GB minimum (16 GB recommended for development)
- **Storage**: 20 GB free disk space for application, databases, and dependencies
- **Network**: Stable internet connection for API calls and cloud services
- **Display**: 1920x1080 resolution minimum for optimal UI experience

#### Server Requirements (Production)
- **CPU**: 4+ cores, 2.5 GHz or higher
- **RAM**: 16 GB minimum (32 GB recommended for high traffic)
- **Storage**: 100 GB SSD for database and file storage
- **Network**: 100 Mbps bandwidth minimum
- **Operating System**: Linux (Ubuntu 20.04+ recommended) or Windows Server 2019+

#### Database Server Requirements
- **PostgreSQL Server**: 4 GB RAM, 50 GB storage
- **MongoDB Server**: 4 GB RAM, 50 GB storage
- **Redis Server**: 2 GB RAM (for caching)

#### Client Requirements
- **Web Browser**: Chrome 90+, Firefox 88+, Safari 14+, or Edge 90+
- **JavaScript**: Enabled
- **Screen Resolution**: 1366x768 minimum (1920x1080 recommended)

---

## 3. Functional Requirements

### 3.1 Admin Module Functionalities

#### 3.1.1 Course Management
- **Create Course**: Admin can create new courses with course code, name, credits, course type (CORE, ELECTIVE, LAB), and description.
- **Add Course Units**: Admin can add units to courses manually with unit number, unit name, and topics (as JSON array or comma-separated).
- **Edit Course**: Admin can update course details including name, credits, and description.
- **Edit Units**: Admin can modify unit information including unit name and topics.
- **Delete Units**: Admin can soft-delete units (mark as inactive).
- **View Courses**: Admin can view all courses in a list with their details.

#### 3.1.2 Question Paper Upload
- **Upload File**: Admin can upload question papers in PDF or DOCX format.
- **Metadata Submission**: Admin must provide course code, exam type (CIE 1, CIE 2, Improvement CIE, SEE), and exam date.
- **Duplicate Detection**: System automatically checks if a question paper with the same course code, exam type, and exam date already exists and prevents duplicate uploads.
- **Processing Status**: Real-time display of processing status (UPLOADED, METADATA_PENDING, PROCESSING, COMPLETED, FAILED) with progress percentage.
- **File Validation**: System validates file format and size before accepting uploads.

#### 3.1.3 AI Processing Pipeline
- **File Conversion**: System converts PDF/DOCX files to text and extracts embedded images for LLM processing.
- **Question Extraction**: OpenAI API extracts questions, marks, and Bloom's taxonomy levels from converted content, handling subparts (2.a, 2.b) as separate records.
- **Question Classification**: LLM classifies extracted questions into appropriate course units and generates topic tags based on syllabus.
- **Image Extraction**: System identifies and extracts diagrams/tables from question papers for display with questions.

#### 3.1.4 Review Queue Management
- **View Review Queue**: Admin can view all non-reviewed questions in a dedicated review queue with priority indicators.
- **Question Details**: Display question text, marks, Bloom's taxonomy, unit, course code, topic tags, and associated images.
- **Edit Question**: Admin can edit unit assignment, topic tags, marks, and Bloom's taxonomy level for questions.
- **Upload Question Image**: Admin can upload or replace images/diagrams for specific questions.
- **Approve Question**: Admin can approve questions, marking them as reviewed and approved.
- **Reject/Correct Question**: Admin can mark questions as needing review with corrections.

#### 3.1.5 Question Bank Management
- **View All Questions**: Admin can browse all questions in the system with pagination.
- **Advanced Search**: Filter questions by course codes, unit IDs, marks range, Bloom's levels, exam types, academic years, review status, and topic tags.
- **Question Details**: View complete question metadata including review status, images, and classification confidence.

#### 3.1.6 Upload Management
- **View Uploads**: Admin can view all uploaded question papers with their processing status.
- **Delete Uploads**: Admin can delete question papers and associated questions.
- **Retry Processing**: Admin can manually retry processing for failed or stuck uploads.

### 3.2 Student Module Functionalities

#### 3.2.1 Course Selection
- **Select Courses**: Students can select their enrolled courses from a list of available courses.
- **Save Selection**: Selected courses are persisted in the database and displayed on the dashboard.
- **View My Courses**: Dashboard displays selected courses with quick access to course-specific questions.

#### 3.2.2 Question Search & Browse
- **Text Search**: Students can search questions by keywords in question text.
- **Browse All**: Students can browse all available questions without entering a search query.
- **Advanced Filters**:
  - **Course Filter**: Select multiple courses to filter questions.
  - **Unit Filter**: When courses are selected, units appear as clickable badges for filtering.
  - **Marks Range**: Filter by minimum and maximum marks.
  - **Bloom's Taxonomy**: Filter by cognitive levels (L1-L6).
  - **Exam Types**: Filter by CIE 1, CIE 2, Improvement CIE, or SEE.
  - **Academic Year**: Filter by year range.
  - **Review Status**: Filter by reviewed, non-reviewed, or all questions.
- **Pagination**: Results are paginated with 20 questions per page.
- **Question Display**: Each question card shows question text, course code, unit, marks, Bloom's level, topic tags, review status badge, and associated images.

#### 3.2.3 Bookmark Functionality
- **Bookmark Questions**: Students can bookmark questions for later reference.
- **View Bookmarks**: Dedicated bookmarks page displays all bookmarked questions.
- **Remove Bookmarks**: Students can remove questions from bookmarks.

#### 3.2.4 Practice Mode
- **Random Questions**: Students can practice with randomly selected questions from their selected courses.
- **Customizable Practice**: Filter practice questions by unit, Bloom's level, and count.

#### 3.2.5 Question Papers Access
- **View Papers**: Students can view a list of uploaded question papers filtered by their selected courses.
- **Download Papers**: Students can download original PDF/DOCX files of question papers.

### 3.3 Authentication & Authorization

#### 3.3.1 Admin Authentication
- **Username/Password Login**: Admins authenticate using username and password.
- **Session Management**: JWT tokens for secure session management.
- **Role-Based Access**: Admin role grants access to all administrative functions.

#### 3.3.2 Student Authentication
- **Google OAuth Login**: Students can log in using their Google accounts.
- **Profile Integration**: System retrieves student profile picture and display name from Google.
- **Session Management**: JWT tokens for secure session management.
- **Role-Based Access**: Student role grants access to student-specific functions only.

### 3.4 System Features

#### 3.4.1 Activity Logging
- **User Activity Tracking**: System logs all significant user actions (uploads, approvals, edits, etc.).
- **Activity History**: Admin can view activity logs for audit purposes.

#### 3.4.2 Dark Mode Support
- **Theme Toggle**: Both admin and student interfaces support dark/light mode switching.
- **Consistent Styling**: All pages maintain consistent dark mode styling.

#### 3.4.3 Error Handling
- **Graceful Error Handling**: System handles errors gracefully with user-friendly error messages.
- **Toast Notifications**: Real-time feedback for all user actions (success, error, warning).

---

## 4. Relational Schema and Normalization

### 4.1 Entity-Relationship Diagram

```
┌─────────────┐         ┌──────────────────┐         ┌──────────────┐
│    Users    │         │  QuestionPapers   │         │  Questions   │
├─────────────┤         ├──────────────────┤         ├──────────────┤
│ user_id (PK)│◄────┐   │ paper_id (PK)    │◄────────│ question_id  │
│ username    │     │   │ course_code (FK) │         │   (PK)       │
│ email       │     │   │ academic_year    │         │ paper_id (FK)│
│ password_hash│    │   │ semester_type    │         │ course_code  │
│ role        │     │   │ exam_type        │         │   (FK)       │
│ branch_id   │     │   │ exam_date        │         │ unit_id (FK) │
│ is_active   │     │   │ uploaded_by (FK) │         │ question_text│
└─────────────┘     │   │ processing_status│         │ marks        │
                    │   └──────────────────┘         │ bloom_level  │
┌─────────────┐     │                                │ image_path   │
│  Branches   │     │                                │ topic_tags   │
├─────────────┤     │                                │ is_reviewed  │
│ branch_id(PK)│    │                                └──────────────┘
│ branch_name │     │                                         │
└─────────────┘     │                                         │
                    │                                         │
┌─────────────┐     │                                ┌──────────────┐
│   Courses   │     │                                │ CourseUnits  │
├─────────────┤     │                                ├──────────────┤
│ course_code │◄────┼────────────────────────────────│ unit_id (PK) │
│   (PK)      │     │                                │ course_code  │
│ course_name │     │                                │   (FK)       │
│ credits     │     │                                │ unit_number  │
│ course_type │     │                                │ unit_name    │
│ is_active   │     │                                │ topics       │
└─────────────┘     │                                └──────────────┘
                    │
┌──────────────────┐│
│ StudentBookmarks ││
├──────────────────┤│
│ bookmark_id (PK) ││
│ student_id (FK)  │┼──┐
│ question_id (FK) │┼──┼──┐
│ notes            │  │  │
└──────────────────┘  │  │
                       │  │
┌──────────────────────┐│  │
│StudentCourseSelection││  │
├──────────────────────┤│  │
│ selection_id (PK)    ││  │
│ student_id (FK)      │┼──┘
│ course_code (FK)     │┼───┐
│ selected_at          │    │
└──────────────────────┘    │
                            │
┌──────────────────────┐    │
│   ReviewQueue        │    │
├──────────────────────┤    │
│ review_id (PK)       │    │
│ question_id (FK)     │┼───┘
│ issue_type           │
│ suggested_correction │
│ priority             │
│ status               │
└──────────────────────┘
```

### 4.2 Database Schema Description

#### 4.2.1 Users Table
**Purpose**: Stores user information for both administrators and students.

**Attributes**:
- `user_id` (INTEGER, PRIMARY KEY): Unique identifier for each user
- `username` (VARCHAR(50), UNIQUE, NOT NULL): Unique username for login
- `email` (VARCHAR(100), UNIQUE, NOT NULL): User email address
- `password_hash` (VARCHAR(255), NULLABLE): Hashed password (nullable for OAuth users)
- `profile_picture_url` (VARCHAR(500), NULLABLE): URL to user's profile picture
- `display_name` (VARCHAR(100), NULLABLE): User's display name
- `role` (VARCHAR(20), NOT NULL): User role (ADMIN or STUDENT)
- `branch_id` (INTEGER, FOREIGN KEY → branches.branch_id, NULLABLE): Associated branch
- `academic_year` (INTEGER, NULLABLE): Academic year (1-4)
- `is_active` (BOOLEAN, DEFAULT TRUE): Account status
- `created_at` (TIMESTAMP): Account creation timestamp
- `updated_at` (TIMESTAMP): Last update timestamp

**Normalization**: 3NF - All attributes are atomic, no partial dependencies, no transitive dependencies.

#### 4.2.2 Courses Table
**Purpose**: Stores course information including course code, name, credits, and type.

**Attributes**:
- `course_code` (VARCHAR(10), PRIMARY KEY): Unique course identifier
- `course_name` (VARCHAR(200), NOT NULL): Full course name
- `credits` (INTEGER, NOT NULL): Credit hours for the course
- `course_type` (VARCHAR(20), NOT NULL): Type (CORE, ELECTIVE, LAB)
- `description` (TEXT, NULLABLE): Course description
- `is_active` (BOOLEAN, DEFAULT TRUE): Course status
- `created_at` (TIMESTAMP): Creation timestamp
- `updated_at` (TIMESTAMP): Last update timestamp

**Normalization**: 3NF - Single primary key, no repeating groups, fully normalized.

#### 4.2.3 CourseUnits Table
**Purpose**: Stores unit information for each course, including unit number, name, and topics.

**Attributes**:
- `unit_id` (INTEGER, PRIMARY KEY): Unique unit identifier
- `course_code` (VARCHAR(10), FOREIGN KEY → courses.course_code, NOT NULL): Associated course
- `unit_number` (INTEGER, NOT NULL): Unit number within the course
- `unit_name` (VARCHAR(200), NOT NULL): Unit name/title
- `topics` (TEXT, NULLABLE): JSON array or comma-separated list of topics
- `is_active` (BOOLEAN, DEFAULT TRUE): Unit status
- `created_at` (TIMESTAMP): Creation timestamp

**Normalization**: 3NF - Properly normalized with foreign key relationship to courses.

#### 4.2.4 QuestionPapers Table
**Purpose**: Stores metadata about uploaded question papers.

**Attributes**:
- `paper_id` (INTEGER, PRIMARY KEY): Unique paper identifier
- `course_code` (VARCHAR(10), FOREIGN KEY → courses.course_code, NOT NULL): Associated course
- `academic_year` (INTEGER, NOT NULL): Academic year (1-4)
- `semester_type` (ENUM: ODD/EVEN, NOT NULL): Semester type
- `exam_type` (ENUM: CIE_1/CIE_2/IMPROVEMENT_CIE/SEE, NOT NULL): Type of examination
- `exam_date` (DATE, NULLABLE): Date of examination
- `pdf_path` (VARCHAR(500), NULLABLE): Permanent storage path for PDF
- `temp_pdf_path` (VARCHAR(500), NULLABLE): Temporary upload path
- `uploaded_by` (INTEGER, FOREIGN KEY → users.user_id, NOT NULL): Admin who uploaded
- `processing_status` (ENUM, DEFAULT UPLOADED): Current processing status
- `processing_progress` (FLOAT, DEFAULT 0.0): Processing progress percentage
- `total_questions_extracted` (INTEGER, DEFAULT 0): Number of questions extracted
- `questions_in_review` (INTEGER, DEFAULT 0): Number of questions pending review
- `file_size` (INTEGER, NULLABLE): File size in bytes
- `page_count` (INTEGER, NULLABLE): Number of pages in the document
- `created_at` (TIMESTAMP): Upload timestamp
- `updated_at` (TIMESTAMP): Last update timestamp

**Normalization**: 3NF - All attributes are atomic and properly normalized. Composite unique constraint on (course_code, exam_type, exam_date) prevents duplicates.

#### 4.2.5 Questions Table
**Purpose**: Stores individual questions extracted from question papers.

**Attributes**:
- `question_id` (INTEGER, PRIMARY KEY): Unique question identifier
- `paper_id` (INTEGER, FOREIGN KEY → question_papers.paper_id, NOT NULL): Associated paper
- `course_code` (VARCHAR(10), FOREIGN KEY → courses.course_code, NOT NULL): Associated course
- `unit_id` (INTEGER, FOREIGN KEY → course_units.unit_id, NULLABLE): Classified unit
- `question_number` (VARCHAR(20), NOT NULL): Question number (e.g., "1", "2a", "3(ii)")
- `question_text` (TEXT, NOT NULL): Full question text
- `marks` (INTEGER, NULLABLE): Marks allocated to the question
- `bloom_level` (ENUM: 1-6, NULLABLE): Bloom's taxonomy level
- `bloom_category` (ENUM, NULLABLE): Bloom's category name
- `bloom_confidence` (FLOAT, NULLABLE): Classification confidence score
- `difficulty_level` (ENUM: EASY/MEDIUM/HARD, NULLABLE): Difficulty assessment
- `classification_confidence` (FLOAT, NULLABLE): Unit classification confidence
- `is_canonical` (BOOLEAN, DEFAULT TRUE): Whether this is the canonical version
- `parent_question_id` (INTEGER, FOREIGN KEY → questions.question_id, NULLABLE): Parent question for subparts
- `similarity_score` (FLOAT, NULLABLE): Similarity score for duplicate detection
- `topic_tags` (TEXT, NULLABLE): JSON array of topic tags
- `image_path` (VARCHAR(500), NULLABLE): Path to associated image/diagram
- `is_reviewed` (BOOLEAN, DEFAULT FALSE): Review status
- `review_status` (ENUM: PENDING/APPROVED/NEEDS_REVIEW, NULLABLE): Review status
- `created_at` (TIMESTAMP): Creation timestamp
- `updated_at` (TIMESTAMP): Last update timestamp

**Normalization**: 3NF - Properly normalized with foreign keys. Self-referential relationship for subparts.

#### 4.2.6 StudentBookmarks Table
**Purpose**: Stores bookmarked questions for students.

**Attributes**:
- `bookmark_id` (INTEGER, PRIMARY KEY): Unique bookmark identifier
- `student_id` (INTEGER, FOREIGN KEY → users.user_id, NOT NULL): Student who bookmarked
- `question_id` (INTEGER, FOREIGN KEY → questions.question_id, NOT NULL): Bookmarked question
- `notes` (TEXT, NULLABLE): Student notes for the bookmark
- `bookmarked_at` (TIMESTAMP, DEFAULT NOW): Bookmark creation timestamp

**Normalization**: 3NF - Composite unique constraint on (student_id, question_id) prevents duplicate bookmarks.

#### 4.2.7 StudentCourseSelection Table
**Purpose**: Stores courses selected by students.

**Attributes**:
- `selection_id` (INTEGER, PRIMARY KEY): Unique selection identifier
- `student_id` (INTEGER, FOREIGN KEY → users.user_id, NOT NULL): Student who selected
- `course_code` (VARCHAR(10), FOREIGN KEY → courses.course_code, NOT NULL): Selected course
- `selected_at` (TIMESTAMP, DEFAULT NOW): Selection timestamp

**Normalization**: 3NF - Composite unique constraint on (student_id, course_code) ensures one selection per student per course.

#### 4.2.8 ReviewQueue Table
**Purpose**: Stores questions pending review by administrators.

**Attributes**:
- `review_id` (INTEGER, PRIMARY KEY): Unique review entry identifier
- `question_id` (INTEGER, FOREIGN KEY → questions.question_id, NOT NULL): Question to review
- `issue_type` (VARCHAR(50), NOT NULL): Type of issue (AMBIGUOUS_UNIT, LOW_CONFIDENCE, NEEDS_REVIEW)
- `suggested_correction` (JSON, NULLABLE): Suggested corrections from AI
- `priority` (INTEGER, NOT NULL): Review priority (1-5, higher is more urgent)
- `status` (VARCHAR(20), DEFAULT PENDING): Review status (PENDING, APPROVED, REJECTED)
- `created_at` (TIMESTAMP, DEFAULT NOW): Review entry creation timestamp

**Normalization**: 3NF - Properly normalized with foreign key to questions.

#### 4.2.9 CourseEquivalence Table
**Purpose**: Stores equivalent course relationships.

**Attributes**:
- `equivalence_id` (INTEGER, PRIMARY KEY): Unique equivalence identifier
- `primary_course_code` (VARCHAR(10), FOREIGN KEY → courses.course_code, NOT NULL): Primary course
- `equivalent_course_code` (VARCHAR(10), FOREIGN KEY → courses.course_code, NOT NULL): Equivalent course
- `reason` (VARCHAR(200), NULLABLE): Reason for equivalence
- `is_active` (BOOLEAN, DEFAULT TRUE): Equivalence status
- `created_at` (TIMESTAMP): Creation timestamp

**Normalization**: 3NF - Properly normalized with foreign keys to courses.

#### 4.2.10 CourseOffering Table
**Purpose**: Stores course offerings by branch and academic year.

**Attributes**:
- `offering_id` (INTEGER, PRIMARY KEY): Unique offering identifier
- `course_code` (VARCHAR(10), FOREIGN KEY → courses.course_code, NOT NULL): Offered course
- `branch_id` (INTEGER, FOREIGN KEY → branches.branch_id, NOT NULL): Branch offering the course
- `academic_year` (INTEGER, NOT NULL): Academic year (1-4)
- `semester_type` (VARCHAR(10), NOT NULL): Semester type (ODD/EVEN)
- `is_active` (BOOLEAN, DEFAULT TRUE): Offering status
- `created_at` (TIMESTAMP): Creation timestamp

**Normalization**: 3NF - Properly normalized with foreign keys.

#### 4.2.11 ActivityLog Table
**Purpose**: Stores user activity logs for audit purposes.

**Attributes**:
- `log_id` (INTEGER, PRIMARY KEY): Unique log identifier
- `user_id` (INTEGER, FOREIGN KEY → users.user_id, NOT NULL): User who performed action
- `activity_type` (VARCHAR(50), NOT NULL): Type of activity
- `description` (TEXT, NULLABLE): Activity description
- `entity_type` (VARCHAR(50), NULLABLE): Type of entity affected
- `entity_id` (VARCHAR(50), NULLABLE): ID of entity affected
- `metadata` (JSON, NULLABLE): Additional metadata
- `created_at` (TIMESTAMP, DEFAULT NOW): Activity timestamp

**Normalization**: 3NF - Properly normalized with foreign key to users.

### 4.3 Normalization Analysis

#### 4.3.1 First Normal Form (1NF)
All tables satisfy 1NF:
- All attributes contain atomic values (no multi-valued attributes)
- No repeating groups
- Each row is unique

#### 4.3.2 Second Normal Form (2NF)
All tables satisfy 2NF:
- All tables are in 1NF
- All non-key attributes are fully functionally dependent on the primary key
- No partial dependencies exist

#### 4.3.3 Third Normal Form (3NF)
All tables satisfy 3NF:
- All tables are in 2NF
- No transitive dependencies exist
- All non-key attributes are directly dependent on the primary key

#### 4.3.4 Boyce-Codd Normal Form (BCNF)
All tables satisfy BCNF:
- All tables are in 3NF
- Every determinant is a candidate key
- No overlapping candidate keys with different attributes

### 4.4 Key Relationships

1. **Users → QuestionPapers**: One-to-Many (One admin can upload many papers)
2. **Courses → QuestionPapers**: One-to-Many (One course can have many papers)
3. **QuestionPapers → Questions**: One-to-Many (One paper contains many questions)
4. **Courses → CourseUnits**: One-to-Many (One course has many units)
5. **CourseUnits → Questions**: One-to-Many (One unit can have many questions)
6. **Users → StudentBookmarks**: One-to-Many (One student can bookmark many questions)
7. **Questions → StudentBookmarks**: One-to-Many (One question can be bookmarked by many students)
8. **Users → StudentCourseSelection**: One-to-Many (One student can select many courses)
9. **Courses → StudentCourseSelection**: One-to-Many (One course can be selected by many students)
10. **Questions → ReviewQueue**: One-to-One (One question can have one review entry)
11. **Questions → Questions**: Self-referential (Parent-child relationship for subparts)

### 4.5 Indexes and Constraints

#### Primary Keys
- All tables have integer primary keys for efficient indexing
- Course table uses `course_code` as primary key (natural key)

#### Foreign Keys
- All foreign key relationships are properly defined with referential integrity
- Cascade delete is used where appropriate (e.g., deleting a question deletes its bookmarks)

#### Unique Constraints
- `users.username`: Unique username constraint
- `users.email`: Unique email constraint
- `(student_id, question_id)` in StudentBookmarks: Prevents duplicate bookmarks
- `(student_id, course_code)` in StudentCourseSelection: Prevents duplicate course selections
- `(course_code, exam_type, exam_date)` in QuestionPapers: Prevents duplicate paper uploads

#### Indexes
- Primary keys are automatically indexed
- Foreign keys are indexed for join performance
- `users.email` and `users.username` are indexed for login queries
- `questions.course_code` and `questions.unit_id` are indexed for filtering

---

## 5. Conclusion

The QPaper AI - Automated Question Paper Management System represents a comprehensive solution for modernizing question paper management in educational institutions. The system successfully addresses the challenges of manual question paper organization by leveraging artificial intelligence and modern web technologies.

The implementation demonstrates effective database design principles through a fully normalized relational schema that eliminates data redundancy and ensures data integrity. The use of PostgreSQL for structured data, combined with proper indexing and foreign key constraints, ensures optimal query performance even with large datasets.

The integration of OpenAI's LLM API for question extraction and classification significantly reduces manual effort while maintaining accuracy through a robust review workflow. The dual-interface design (admin and student) provides role-appropriate functionality, enhancing both administrative efficiency and student learning experience.

Key achievements include:
- **Automated Processing**: Complete automation of question extraction and classification
- **Scalable Architecture**: Modular design supporting future enhancements
- **User-Centric Design**: Intuitive interfaces with dark mode support and responsive design
- **Data Integrity**: Comprehensive normalization and constraint enforcement
- **Security**: Role-based access control and secure authentication mechanisms

The system is production-ready and can be easily extended to support additional features such as analytics, reporting, and integration with Learning Management Systems (LMS). The use of Docker containerization ensures easy deployment and scalability across different environments.

---

## 6. References

[1] FastAPI Documentation. (2023). *FastAPI - Modern, Fast Web Framework for Building APIs*. Retrieved from https://fastapi.tiangolo.com/

[2] PostgreSQL Global Development Group. (2023). *PostgreSQL 14 Documentation*. Retrieved from https://www.postgresql.org/docs/14/

[3] MongoDB Inc. (2023). *MongoDB Manual 6.0*. Retrieved from https://www.mongodb.com/docs/manual/

[4] OpenAI. (2023). *OpenAI API Documentation*. Retrieved from https://platform.openai.com/docs

[5] Next.js Team. (2023). *Next.js Documentation*. Retrieved from https://nextjs.org/docs

[6] React Team. (2023). *React Documentation*. Retrieved from https://react.dev/

[7] SQLAlchemy Project. (2023). *SQLAlchemy 2.0 Documentation*. Retrieved from https://docs.sqlalchemy.org/en/20/

[8] Silberschatz, A., Korth, H. F., & Sudarshan, S. (2019). *Database System Concepts* (7th ed.). McGraw-Hill Education.

[9] Connolly, T., & Begg, C. (2015). *Database Systems: A Practical Approach to Design, Implementation, and Management* (6th ed.). Pearson.

[10] Elmasri, R., & Navathe, S. B. (2016). *Fundamentals of Database Systems* (7th ed.). Pearson.

[11] Tanenbaum, A. S., & Wetherall, D. J. (2011). *Computer Networks* (5th ed.). Prentice Hall.

[12] Docker Inc. (2023). *Docker Documentation*. Retrieved from https://docs.docker.com/

[13] Redis Labs. (2023). *Redis Documentation*. Retrieved from https://redis.io/docs/

[14] Tailwind Labs. (2023). *Tailwind CSS Documentation*. Retrieved from https://tailwindcss.com/docs

[15] IEEE Computer Society. (2014). *IEEE Std 1012-2012 - IEEE Standard for System and Software Verification and Validation*. IEEE.

---

## 7. Appendix: Snapshots

### Screenshots to Include

#### 7.1 Admin Interface Screenshots

1. **Admin Login Page**
   - Screenshot of the admin login interface
   - Shows username/password fields and login button

2. **Admin Dashboard**
   - Overview of the admin dashboard
   - Quick action cards (Upload Question Paper, Question Bank, Manage Courses, Manage Uploads)
   - Statistics cards showing total questions, papers, etc.

3. **Course Management Page**
   - List of all courses with course codes, names, and credits
   - Add Course modal/form
   - Edit Course functionality
   - Unit management (Add Unit, Edit Unit, Delete Unit)

4. **Question Paper Upload Page**
   - File upload interface
   - Metadata form (course code dropdown, exam type, exam date)
   - Processing status display with progress bar

5. **Review Queue Page**
   - List of questions pending review
   - Question details panel showing question text, marks, Bloom's taxonomy, unit, topic tags
   - Edit question modal
   - Image upload interface
   - Approve/Reject buttons

6. **Question Bank Page**
   - Search interface with filters
   - Question list with pagination
   - Question cards showing all metadata
   - Review button linking to review queue

7. **Manage Uploads Page**
   - List of all uploaded question papers
   - Processing status indicators
   - Delete/Retry options

#### 7.2 Student Interface Screenshots

8. **Student Login Page**
   - Google OAuth login button
   - Student login interface

9. **Student Dashboard**
   - Quick action cards (Search Questions, My Bookmarks, Practice Mode, My Courses)
   - My Courses section showing selected courses
   - Course selection prompt if no courses selected

10. **My Courses Page**
    - List of available courses with checkboxes
    - Selected courses highlighted
    - Save button

11. **Search Questions Page**
    - Search bar
    - Filters panel (Course, Units as badges, Marks Range, Bloom's Level, Exam Types, Review Status)
    - Question cards with images (if available)
    - Pagination controls
    - Bookmark button on each question

12. **Question Card with Image**
    - Detailed view of a question card
    - Question image/diagram displayed
    - Topic tags as badges
    - All metadata visible (marks, Bloom's level, review status)

13. **My Bookmarks Page**
    - List of bookmarked questions
    - Remove bookmark functionality

14. **Practice Mode Page**
    - Random question display
    - Filter options for practice questions

15. **Question Papers Page**
    - List of available question papers
    - Download buttons for each paper
    - Filtered by selected courses

#### 7.3 Database Schema Screenshots

16. **Database Schema Diagram**
    - ER diagram showing all tables and relationships
    - Can be generated using database tools or drawn using tools like draw.io

17. **Table Structure Screenshots**
    - Screenshots of key tables in PostgreSQL (using pgAdmin or similar tool)
    - Show columns, data types, constraints
    - Include: users, courses, questions, question_papers tables

18. **Sample Data Screenshots**
    - Screenshots showing sample data in tables
    - Demonstrate relationships between tables
    - Show foreign key relationships

#### 7.4 System Architecture Screenshots

19. **API Documentation**
    - Screenshot of FastAPI auto-generated Swagger/OpenAPI documentation
    - Show available endpoints

20. **Processing Pipeline**
    - Screenshot showing question paper processing flow
    - Can be a diagram or console output showing processing steps

#### 7.5 Additional Screenshots

21. **Dark Mode Interface**
    - Screenshot of any page in dark mode
    - Show theme toggle button

22. **Error Handling**
    - Screenshot of error messages/toast notifications
    - Show user-friendly error handling

23. **Mobile Responsive View** (Optional)
    - Screenshot of interface on mobile/tablet view
    - Show responsive design

### Screenshot Guidelines

- **Resolution**: Use 1920x1080 or higher resolution
- **Format**: PNG or JPG format
- **Annotations**: Add arrows, labels, or highlights to point out key features
- **Consistency**: Use consistent browser/theme across all screenshots
- **Quality**: Ensure text is readable and UI elements are clear
- **Organization**: Number screenshots sequentially (Screenshot 1, Screenshot 2, etc.)
- **Captions**: Add brief captions explaining what each screenshot demonstrates

---

**Document Version**: 1.0  
**Last Updated**: 2024  
**Author**: [Your Name]  
**Institution**: [Your Institution Name]


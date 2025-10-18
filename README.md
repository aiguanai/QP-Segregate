# QPaper AI - Automated Question Paper Management System

An intelligent system for extracting, classifying, and organizing university question papers using OCR, NLP, and ML technologies.

## Features

- **Two-step PDF upload process** with metadata form
- **Intelligent question extraction** using OCR and NLP
- **Semantic question deduplication** with similarity grouping
- **Bloom taxonomy classification** for cognitive levels
- **Course-centric model** with equivalence handling
- **Dual interface system** for admins and students
- **Real-time processing status** with background tasks

## Tech Stack

- **Backend**: Python FastAPI, Celery, Redis
- **Frontend**: React, Next.js, Tailwind CSS
- **Databases**: PostgreSQL, MongoDB, Pinecone/Qdrant
- **AI/ML**: Tesseract OCR, spaCy, Sentence-BERT
- **Storage**: AWS S3 or local storage
- **Deployment**: Docker + Docker Compose

## Quick Start

1. Clone the repository
2. Run `docker-compose up` to start all services
3. Access admin interface at `http://localhost:3000/admin`
4. Access student interface at `http://localhost:3000/student`

## Project Structure

```
QPseg/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Core functionality
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   └── tasks/          # Celery tasks
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # React/Next.js frontend
│   ├── src/
│   │   ├── components/     # Reusable components
│   │   ├── pages/          # Page components
│   │   └── services/       # API services
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## Development

### Backend Development
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

## License

MIT License

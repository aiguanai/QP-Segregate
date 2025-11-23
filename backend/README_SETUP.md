# Backend Setup Guide

## Quick Start

### 1. Create Virtual Environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
python -c "import spacy; spacy.cli.download('en_core_web_sm')"
```

### 3. Configure Environment

Copy `env.example` to `.env` and update with your cloud database URLs:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.YOUR_PROJECT.supabase.co:5432/postgres
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/qpaper_ai
REDIS_URL=redis://username:password@your-redis-endpoint:port
```

### 4. Test Connections

```powershell
python test_connections.py
```

### 5. Initialize Database

```powershell
python init_db.py
```

This will:
- Create all database tables
- Create admin user (username: `admin`, password: `admin123`)
- Create sample courses

### 6. Run Backend

```powershell
uvicorn app.main:app --reload
```

Backend will be available at: http://localhost:8000

## Testing

### Test Supabase Connection
```powershell
python ..\test_supabase.py
```

### Test All Database Connections
```powershell
python test_connections.py
```

## File Structure

- `app/` - Application code
- `app/core/` - Core configuration and database
- `app/models/` - Database models
- `app/api/` - API endpoints
- `app/services/` - Business logic
- `app/tasks/` - Celery background tasks
- `.env` - Environment variables (create from env.example)
- `requirements.txt` - Python dependencies

## Environment Variables

Required:
- `DATABASE_URL` - PostgreSQL connection string (Supabase)

Optional:
- `MONGODB_URL` - MongoDB connection string
- `REDIS_URL` - Redis connection string
- `JWT_SECRET_KEY` - Secret key for JWT tokens
- `PINECONE_API_KEY` - Pinecone API key (for vector search)

## Troubleshooting

### Module not found
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt`

### Database connection failed
- Check your `.env` file has correct `DATABASE_URL`
- Verify your Supabase project is active
- Test connection with `test_connections.py`

### spaCy model not found
- Run: `python -c "import spacy; spacy.cli.download('en_core_web_sm')"`


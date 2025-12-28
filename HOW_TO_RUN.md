# How to Run QPaper AI Project

This guide covers all ways to run the project, from easiest to most flexible.

---

## 🚀 Method 1: Docker Compose (Easiest - Recommended)

**Best for**: Quick start, local development, testing

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop) installed
- Docker Desktop running

### Steps

1. **Set up environment file** (if not done):
   ```powershell
   cd backend
   copy env.example .env
   ```
   Edit `backend/.env` and set at minimum:
   ```env
   JWT_SECRET_KEY=your-random-secret-key-here
   ```
   (Database URLs work with Docker defaults)

2. **Start all services**:
   ```powershell
   # From project root
   docker-compose up
   ```
   
   Or run in background:
   ```powershell
   docker-compose up -d
   ```

3. **Wait for services to start** (2-3 minutes first time):
   - PostgreSQL database
   - MongoDB database
   - Redis cache
   - Backend API (FastAPI)
   - Celery worker (background tasks)
   - Frontend (Next.js)

4. **Access the application**:
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs
   - **Admin Login**: http://localhost:3000/admin/login
   - **Student Login**: http://localhost:3000/student/login

5. **Initialize database** (first time only):
   ```powershell
   # In a new terminal
   docker-compose exec backend python init_db.py
   ```
   
   This creates:
   - Database tables
   - Admin user: `admin` / `admin123`
   - Student user: `student` / `student123`
   - Sample courses

6. **Stop services**:
   ```powershell
   docker-compose down
   ```

### What's Running?
- ✅ PostgreSQL (port 5432)
- ✅ MongoDB (port 27017)
- ✅ Redis (port 6379)
- ✅ Backend API (port 8000)
- ✅ Frontend (port 3000)
- ✅ Celery Worker (background processing)

---

## 🛠️ Method 2: Manual Setup (Development Mode)

**Best for**: Active development, debugging, customization

### Prerequisites
- Python 3.9+ installed
- Node.js 16+ installed
- PostgreSQL, MongoDB, Redis running (or use Docker for just databases)

### Steps

#### Part A: Database Setup (Choose One)

**Option 1: Use Docker for databases only**
```powershell
# Start only databases
docker-compose up postgres mongodb redis -d
```

**Option 2: Use cloud databases**
- Follow `backend/ENV_SETUP_GUIDE.md` to set up Supabase, MongoDB Atlas, Redis Cloud

#### Part B: Backend Setup

1. **Navigate to backend**:
   ```powershell
   cd backend
   ```

2. **Create virtual environment**:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   python -c "import spacy; spacy.cli.download('en_core_web_sm')"
   ```

4. **Set up environment**:
   ```powershell
   copy env.example .env
   notepad .env
   ```
   
   Update with your database URLs (or use localhost if using Docker for DBs):
   ```env
   DATABASE_URL=postgresql://qpaper_user:qpaper_password@localhost:5432/qpaper_ai
   MONGODB_URL=mongodb://qpaper_user:qpaper_password@localhost:27017/qpaper_ai?authSource=admin
   REDIS_URL=redis://localhost:6379
   JWT_SECRET_KEY=your-random-secret-key-here
   ```

5. **Test connections**:
   ```powershell
   python test_connections.py
   ```

6. **Initialize database**:
   ```powershell
   python init_db.py
   ```

7. **Start backend** (Terminal 1):
   ```powershell
   uvicorn app.main:app --reload
   ```
   Backend runs at: http://localhost:8000

8. **Start Celery worker** (Terminal 2):
   ```powershell
   cd backend
   .\venv\Scripts\Activate.ps1
   celery -A app.tasks.celery worker --loglevel=info
   ```

#### Part C: Frontend Setup

1. **Navigate to frontend**:
   ```powershell
   cd frontend
   ```

2. **Install dependencies**:
   ```powershell
   npm install
   ```

3. **Create environment file** (if needed):
   ```powershell
   echo NEXT_PUBLIC_API_URL=http://localhost:8000 > .env.local
   ```

4. **Start frontend** (Terminal 3):
   ```powershell
   npm run dev
   ```
   Frontend runs at: http://localhost:3000

### You Need 3 Terminals Running:
- **Terminal 1**: Backend API (`uvicorn app.main:app --reload`)
- **Terminal 2**: Celery Worker (`celery -A app.tasks.celery worker`)
- **Terminal 3**: Frontend (`npm run dev`)

---

## ☁️ Method 3: Cloud Setup (Production-like)

**Best for**: Production deployment, cloud testing, no local databases

### Steps

1. **Set up cloud databases**:
   - Follow `backend/ENV_SETUP_GUIDE.md` for:
     - Supabase (PostgreSQL)
     - MongoDB Atlas
     - Redis Cloud

2. **Configure environment**:
   ```powershell
   cd backend
   copy env.example .env
   notepad .env
   ```
   
   Update with cloud URLs:
   ```env
   DATABASE_URL=postgresql://postgres:password@db.project.supabase.co:5432/postgres
   MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/qpaper_ai?retryWrites=true&w=majority
   REDIS_URL=redis://user:pass@redis-endpoint:port
   JWT_SECRET_KEY=your-secret-key
   ```

3. **Run setup script**:
   ```powershell
   # From project root
   .\setup-now.bat
   ```
   
   Or manually:
   ```powershell
   cd backend
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   python -c "import spacy; spacy.cli.download('en_core_web_sm')"
   python init_db.py
   ```

4. **Start services** (same as Method 2):
   - Backend: `uvicorn app.main:app --reload`
   - Celery: `celery -A app.tasks.celery worker`
   - Frontend: `npm run dev`

---

## 🎯 Quick Start Commands

### First Time Setup
```powershell
# Option 1: Automated setup (Windows)
.\setup.bat

# Option 2: Manual
cd backend
copy env.example .env
# Edit .env with your values
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python init_db.py
```

### Running the Project

**Docker (Easiest)**:
```powershell
docker-compose up
```

**Manual (Development)**:
```powershell
# Terminal 1: Backend
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload

# Terminal 2: Celery
cd backend
.\venv\Scripts\Activate.ps1
celery -A app.tasks.celery worker --loglevel=info

# Terminal 3: Frontend
cd frontend
npm run dev
```

---

## 🔐 Default Login Credentials

After running `init_db.py`:

- **Admin**:
  - Username: `admin`
  - Password: `admin123`
  - URL: http://localhost:3000/admin/login

- **Student**:
  - Username: `student`
  - Password: `student123`
  - URL: http://localhost:3000/student/login

⚠️ **Change these in production!**

---

## 🧪 Testing

### Test Database Connections
```powershell
cd backend
python test_connections.py
```

### Test API
- Open: http://localhost:8000/docs
- Interactive API documentation (Swagger UI)

### Test Frontend
- Open: http://localhost:3000
- Try logging in with default credentials

---

## 🐛 Troubleshooting

### Port Already in Use
```powershell
# Find what's using the port
netstat -ano | findstr :8000
netstat -ano | findstr :3000

# Kill the process (replace PID)
taskkill /PID <process_id> /F
```

### Docker Issues
```powershell
# Restart Docker Desktop
# Or rebuild containers
docker-compose down
docker-compose build
docker-compose up
```

### Database Connection Failed
```powershell
# Test connection
cd backend
python test_connections.py

# Check .env file has correct URLs
# Verify databases are running (if local)
docker-compose ps
```

### Module Not Found
```powershell
# Make sure virtual environment is activated
cd backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Frontend Not Connecting to Backend
- Check `frontend/.env.local` has: `NEXT_PUBLIC_API_URL=http://localhost:8000`
- Verify backend is running on port 8000
- Check browser console for CORS errors

### Celery Not Working
- Make sure Redis is running
- Check `REDIS_URL` in `.env` is correct
- Verify Celery worker terminal shows no errors

---

## 📊 Service Ports

| Service | Port | URL |
|---------|------|-----|
| Frontend | 3000 | http://localhost:3000 |
| Backend API | 8000 | http://localhost:8000 |
| API Docs | 8000 | http://localhost:8000/docs |
| PostgreSQL | 5432 | localhost:5432 |
| MongoDB | 27017 | localhost:27017 |
| Redis | 6379 | localhost:6379 |

---

## 🎉 Success Checklist

When everything is running, you should see:

- ✅ Backend API responds at http://localhost:8000/docs
- ✅ Frontend loads at http://localhost:3000
- ✅ Can login as admin/student
- ✅ Database connections work (test with `test_connections.py`)
- ✅ Celery worker is processing tasks (check terminal)

---

## 📚 Next Steps

1. **Upload a question paper** (Admin interface)
2. **Monitor processing** (Admin dashboard)
3. **Search questions** (Student interface)
4. **Review extracted questions** (Admin review page)

---

## 💡 Tips

- **Development**: Use Method 2 (Manual) for hot-reload and debugging
- **Quick Testing**: Use Method 1 (Docker) for everything in one command
- **Production**: Use Method 3 (Cloud) with proper security
- **First Time**: Start with Docker to verify everything works, then switch to manual for development

---

## 🆘 Still Having Issues?

1. Check `backend/ENV_SETUP_GUIDE.md` for environment variable setup
2. Check `backend/README_SETUP.md` for backend-specific setup
3. Check logs in terminal output
4. Verify all prerequisites are installed
5. Try `docker-compose down -v` to reset everything (⚠️ deletes data)


# Quick Start Guide - Cloud Databases Setup

## ✅ Current Status

- ✅ Supabase PostgreSQL: Connected and working
- ✅ Backend dependencies: Installed
- ✅ spaCy model: Installed
- ✅ Storage directories: Created
- ✅ Test scripts: Created
- ⚠️  `.env` file: Needs to be created manually

## 🚀 Quick Start (5 minutes)

### Step 1: Create .env File

```powershell
cd backend
copy env.example .env
notepad .env
```

Update the `DATABASE_URL` line with your Supabase connection:
```env
DATABASE_URL=postgresql://postgres:9MmID8s718tW7qns@db.sjngjegkghyfzdiiukhf.supabase.co:5432/postgres
```

### Step 2: Activate Virtual Environment

```powershell
.\venv\Scripts\Activate.ps1
```

### Step 3: Test Connection

```powershell
python test_connections.py
```

### Step 4: Initialize Database

```powershell
python init_db.py
```

This creates:
- All database tables
- Admin user (username: `admin`, password: `admin123`)
- Sample courses

### Step 5: Run Backend

```powershell
uvicorn app.main:app --reload
```

Backend will be at: http://localhost:8000

## 📋 Next: Set Up MongoDB & Redis

### MongoDB Atlas (5 minutes)

1. Go to https://cloud.mongodb.com
2. Sign up → Build Database → Free tier
3. Create cluster → Create user → Network Access: Allow `0.0.0.0/0`
4. Get connection string
5. Add to `backend/.env`:
   ```env
   MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/qpaper_ai?retryWrites=true&w=majority
   ```

### Redis Cloud (2 minutes)

1. Go to https://redis.com/redis-enterprise-cloud/
2. Sign up → Create database → Free tier
3. Get connection string
4. Add to `backend/.env`:
   ```env
   REDIS_URL=redis://username:password@your-redis-endpoint:port
   ```

## 🧪 Testing Commands

```powershell
# Test Supabase connection
python ..\test_supabase.py

# Test all database connections
python test_connections.py

# Initialize database
python init_db.py

# Run backend
uvicorn app.main:app --reload
```

## 📁 Important Files

- `backend/.env` - **Create this!** Copy from `env.example`
- `backend/test_connections.py` - Test all connections
- `backend/init_db.py` - Initialize database
- `test_supabase.py` - Quick Supabase test

## ⚠️ Important Notes

1. **Always activate venv first**: `.\venv\Scripts\Activate.ps1`
2. **.env file location**: Must be in `backend/` directory
3. **Admin password**: Change `admin123` after first login!

## 🎉 You're Ready!

Once you create the `.env` file and initialize the database, you can start using the application!


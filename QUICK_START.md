# QPaper AI - Quick Start Guide

## 🚀 **Get Running in 5 Minutes**

### **Step 1: Run Setup Script**
```bash
# Windows
setup-now.bat

# This will:
# - Create environment file
# - Install dependencies
# - Create directories
# - Download AI models
```

### **Step 2: Get Cloud Database URLs**

#### **🔵 Supabase (PostgreSQL) - 2 minutes**
1. Go to [supabase.com](https://supabase.com)
2. Click "Start your project"
3. Create new project
4. Go to Settings → Database
5. Copy connection string
6. Edit `backend/.env`:
```env
CLOUD_DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.YOUR_PROJECT.supabase.co:5432/postgres
```

#### **🟢 MongoDB Atlas - 2 minutes**
1. Go to [cloud.mongodb.com](https://cloud.mongodb.com)
2. Create account → Build a Database
3. Choose FREE tier
4. Create cluster
5. Create database user
6. Network Access → Add IP Address → 0.0.0.0/0
7. Database → Connect → Connect your application
8. Copy connection string
9. Edit `backend/.env`:
```env
CLOUD_MONGODB_URL=mongodb+srv://USERNAME:PASSWORD@cluster.mongodb.net/qpaper_ai?retryWrites=true&w=majority
```

#### **🔴 Redis Cloud - 1 minute**
1. Go to [redis.com/redis-enterprise-cloud](https://redis.com/redis-enterprise-cloud/)
2. Sign up → Create database
3. Choose FREE tier
4. Get connection details
5. Edit `backend/.env`:
```env
CLOUD_REDIS_URL=redis://USERNAME:PASSWORD@your-redis-endpoint:port
```

### **Step 3: Start Application**
```bash
# Option 1: Docker (Recommended)
docker-compose -f docker-compose.cloud.no-s3.yml up

# Option 2: Development mode
# Terminal 1: Backend
cd backend
uvicorn app.main:app --reload

# Terminal 2: Frontend  
cd frontend
npm run dev

# Terminal 3: Celery
cd backend
celery -A app.tasks.celery worker --loglevel=info
```

### **Step 4: Access Application**
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### **Step 5: Login**
- **Admin**: username: `admin`, password: `admin123`
- **Student**: username: `student`, password: `student123`

## 🎯 **What You Get**

### **Admin Features:**
- Upload question papers (PDF)
- Fill metadata form
- Monitor processing status
- Review low-confidence questions
- Analytics dashboard

### **Student Features:**
- Search questions semantically
- Filter by course, unit, marks, Bloom level
- View question variants
- Bookmark questions
- Practice mode with random questions

## 🔧 **Troubleshooting**

### **Database Connection Issues:**
```bash
# Test PostgreSQL connection
psql "postgresql://postgres:password@db.project.supabase.co:5432/postgres"

# Test MongoDB connection
mongosh "mongodb+srv://username:password@cluster.mongodb.net/qpaper_ai"

# Test Redis connection
redis-cli -h your-redis-endpoint -p port -a password
```

### **Common Issues:**
1. **"Database connection failed"** → Check your URLs in `.env`
2. **"Module not found"** → Run `pip install -r requirements.txt`
3. **"Port already in use"** → Stop other services or change ports
4. **"Permission denied"** → Run as administrator

### **Reset Everything:**
```bash
# Stop all services
docker-compose down

# Remove volumes (careful - deletes data)
docker-compose down -v

# Restart
docker-compose -f docker-compose.cloud.no-s3.yml up
```

## 📊 **Cost Breakdown**

### **Free Tier (Recommended):**
- **Supabase**: 500MB database (free)
- **MongoDB Atlas**: 512MB (free)  
- **Redis Cloud**: 30MB (free)
- **Storage**: Local (free)
- **Total**: $0/month

### **Production Scale:**
- **Supabase**: $25/month (8GB)
- **MongoDB Atlas**: $57/month (M10 cluster)
- **Redis Cloud**: $7/month (250MB)
- **Storage**: Local (free)
- **Total**: ~$89/month

## 🎉 **You're Ready!**

Your QPaper AI system is now running with:
- ✅ Cloud databases for scalability
- ✅ Local storage (no AWS S3 costs)
- ✅ AI-powered question processing
- ✅ Semantic search and deduplication
- ✅ Admin and student interfaces

Start uploading question papers and see the AI magic happen! 🚀

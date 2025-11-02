# QPaper AI - Cloud Database Setup (Without AWS S3)

This guide shows how to set up QPaper AI with cloud databases but without AWS S3, using local storage or alternative cloud storage options.

## Storage Options (Without AWS S3)

### Option 1: Local Storage (Recommended for Development)
- Store files locally on your server
- Simple setup, no additional costs
- Good for development and small deployments

### Option 2: Google Cloud Storage
- Alternative to AWS S3
- Similar functionality
- Often cheaper than AWS

### Option 3: Supabase Storage
- Built-in with Supabase
- Simple integration
- Free tier available

## Quick Setup (Local Storage)

### 1. Configure Environment

Create `backend/.env` with cloud databases but local storage:

```env
# Cloud Database URLs
CLOUD_DATABASE_URL=postgresql://postgres:password@db.your-project.supabase.co:5432/postgres
CLOUD_MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/qpaper_ai?retryWrites=true&w=majority
CLOUD_REDIS_URL=redis://username:password@your-redis-cloud-endpoint:port

# Local Storage (No AWS S3)
UPLOAD_DIR=storage/papers
TEMP_UPLOAD_DIR=tmp/uploads
PAGE_IMAGES_DIR=storage/page_images

# Security
JWT_SECRET_KEY=your-super-secure-jwt-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# External APIs (Optional)
PINECONE_API_KEY=your-pinecone-api-key
MATHPIX_API_KEY=your-mathpix-api-key

# Processing Configuration
OCR_CONFIDENCE_THRESHOLD=0.4
CLASSIFICATION_CONFIDENCE_THRESHOLD=0.7
SIMILARITY_THRESHOLD=0.85
TEMP_UPLOAD_EXPIRE_HOURS=24
```

### 2. Updated Docker Compose

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      # Cloud database URLs
      - DATABASE_URL=${CLOUD_DATABASE_URL}
      - MONGODB_URL=${CLOUD_MONGODB_URL}
      - REDIS_URL=${CLOUD_REDIS_URL}
      
      # Local storage (no AWS)
      - UPLOAD_DIR=storage/papers
      - TEMP_UPLOAD_DIR=tmp/uploads
      - PAGE_IMAGES_DIR=storage/page_images
      
      # Security
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - JWT_ALGORITHM=HS256
      - ACCESS_TOKEN_EXPIRE_MINUTES=30
      
      # External APIs
      - PINECONE_API_KEY=${PINECONE_API_KEY}
      - MATHPIX_API_KEY=${MATHPIX_API_KEY}
    volumes:
      # Mount local storage
      - ./storage:/app/storage
      - ./tmp:/app/tmp
      - ./logs:/app/logs
    restart: unless-stopped

  celery_worker:
    build: ./backend
    environment:
      - DATABASE_URL=${CLOUD_DATABASE_URL}
      - MONGODB_URL=${CLOUD_MONGODB_URL}
      - REDIS_URL=${CLOUD_REDIS_URL}
      - UPLOAD_DIR=storage/papers
      - TEMP_UPLOAD_DIR=tmp/uploads
      - PAGE_IMAGES_DIR=storage/page_images
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - PINECONE_API_KEY=${PINECONE_API_KEY}
      - MATHPIX_API_KEY=${MATHPIX_API_KEY}
    volumes:
      - ./storage:/app/storage
      - ./tmp:/app/tmp
      - ./logs:/app/logs
    restart: unless-stopped
    command: celery -A app.tasks.celery worker --loglevel=info

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  storage:
  tmp:
  logs:
```

## Alternative: Google Cloud Storage

If you want cloud storage without AWS, use Google Cloud Storage:

### 1. Setup Google Cloud Storage

```bash
# Install Google Cloud SDK
# https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Create storage bucket
gsutil mb gs://your-qpaper-bucket
```

### 2. Environment Configuration

```env
# Cloud Databases
CLOUD_DATABASE_URL=postgresql://postgres:password@db.your-project.supabase.co:5432/postgres
CLOUD_MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/qpaper_ai
CLOUD_REDIS_URL=redis://username:password@your-redis-cloud-endpoint:port

# Google Cloud Storage
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_BUCKET=your-qpaper-bucket
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json

# Storage paths
UPLOAD_DIR=gs://your-qpaper-bucket/papers
TEMP_UPLOAD_DIR=gs://your-qpaper-bucket/temp
PAGE_IMAGES_DIR=gs://your-qpaper-bucket/page_images
```

## Alternative: Supabase Storage

Use Supabase's built-in storage (free tier available):

### 1. Enable Supabase Storage

```sql
-- In Supabase SQL Editor
CREATE POLICY "Public Access" ON storage.objects FOR SELECT USING (true);
CREATE POLICY "Public Upload" ON storage.objects FOR INSERT WITH CHECK (true);
```

### 2. Environment Configuration

```env
# Supabase Database + Storage
CLOUD_DATABASE_URL=postgresql://postgres:password@db.your-project.supabase.co:5432/postgres
CLOUD_MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/qpaper_ai
CLOUD_REDIS_URL=redis://username:password@your-redis-cloud-endpoint:port

# Supabase Storage
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_SERVICE_KEY=your-supabase-service-key

# Storage paths
UPLOAD_DIR=supabase://papers
TEMP_UPLOAD_DIR=supabase://temp
PAGE_IMAGES_DIR=supabase://page_images
```

## Modified Cloud Storage Service

I'll create a version that works without AWS S3:

```python
# backend/app/core/local_cloud_storage.py
import os
import shutil
from typing import Optional
from app.core.config import settings

class LocalCloudStorage:
    """Local storage with cloud database integration"""
    
    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        self.temp_dir = settings.TEMP_UPLOAD_DIR
        self.page_images_dir = settings.PAGE_IMAGES_DIR
        
        # Create directories if they don't exist
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.page_images_dir, exist_ok=True)
    
    def upload_file(self, local_file_path: str, cloud_key: str) -> str:
        """Copy file to local storage and return local URL"""
        try:
            # Create directory structure
            target_path = os.path.join(self.upload_dir, cloud_key)
            target_dir = os.path.dirname(target_path)
            os.makedirs(target_dir, exist_ok=True)
            
            # Copy file
            shutil.copy2(local_file_path, target_path)
            
            # Return local URL
            return f"/storage/{cloud_key}"
            
        except Exception as e:
            raise Exception(f"Local storage upload failed: {e}")
    
    def download_file(self, cloud_key: str, local_path: str) -> str:
        """Copy file from local storage"""
        try:
            source_path = os.path.join(self.upload_dir, cloud_key)
            if os.path.exists(source_path):
                shutil.copy2(source_path, local_path)
                return local_path
            else:
                raise FileNotFoundError(f"File not found: {cloud_key}")
        except Exception as e:
            raise Exception(f"Local storage download failed: {e}")
    
    def delete_file(self, cloud_key: str) -> bool:
        """Delete file from local storage"""
        try:
            file_path = os.path.join(self.upload_dir, cloud_key)
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            raise Exception(f"Local storage delete failed: {e}")
    
    def get_file_url(self, cloud_key: str) -> str:
        """Get local URL for file"""
        return f"/storage/{cloud_key}"
    
    def list_files(self, prefix: str = "") -> list:
        """List files in local storage"""
        try:
            search_path = os.path.join(self.upload_dir, prefix) if prefix else self.upload_dir
            files = []
            
            for root, dirs, filenames in os.walk(search_path):
                for filename in filenames:
                    file_path = os.path.join(root, filename)
                    relative_path = os.path.relpath(file_path, self.upload_dir)
                    files.append(relative_path)
            
            return files
        except Exception as e:
            raise Exception(f"Local storage list failed: {e}")

# Global storage instance
local_cloud_storage = LocalCloudStorage()
```

## Setup Script (No AWS S3)

```bash
# setup-cloud-no-s3.bat
@echo off
echo 🚀 Setting up QPaper AI with Cloud Databases (No AWS S3)
echo ========================================================

echo 📋 Step 1: Copying environment file...
if not exist "backend\.env" (
    copy "env.cloud.no-s3.example" "backend\.env"
    echo ✅ Created backend\.env from template
    echo ⚠️  Please edit backend\.env with your cloud database URLs
) else (
    echo ⚠️  backend\.env already exists
)

echo.
echo 📋 Step 2: Creating local storage directories...
if not exist "storage\papers" mkdir "storage\papers"
if not exist "storage\page_images" mkdir "storage\page_images"
if not exist "tmp\uploads" mkdir "tmp\uploads"
if not exist "logs" mkdir "logs"
echo ✅ Local storage directories created

echo.
echo 📋 Step 3: Installing dependencies...
cd backend
pip install -r requirements.txt
cd ..\frontend
npm install
cd ..

echo.
echo 📋 Step 4: Running database migration...
cd backend
python migrate_to_cloud.py
cd ..

echo.
echo ✅ Setup complete!
echo.
echo 📋 Next steps:
echo 1. Edit backend\.env with your cloud database URLs
echo 2. Start: docker-compose -f docker-compose.cloud.no-s3.yml up
echo 3. Access: http://localhost:3000
echo 4. Login: admin/admin123 or student/student123
pause
```

## Benefits of This Approach

### ✅ **Advantages:**
- **No AWS costs** for storage
- **Simpler setup** - just cloud databases
- **Local file access** - faster for development
- **Easy backup** - just copy the storage folder
- **No vendor lock-in** for storage

### ⚠️ **Considerations:**
- **File size limits** on your server
- **Backup responsibility** - you manage file backups
- **Scaling** - may need cloud storage for production
- **CDN** - no automatic global distribution

## Production Recommendations

For production without AWS S3, consider:

1. **Google Cloud Storage** - Often cheaper than AWS
2. **Supabase Storage** - Built-in with your database
3. **DigitalOcean Spaces** - S3-compatible, cheaper
4. **Cloudflare R2** - Very cost-effective
5. **Local + CDN** - Use CloudFlare or similar for global distribution

This setup gives you cloud databases for scalability while keeping storage simple and cost-effective!

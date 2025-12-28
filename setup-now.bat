@echo off
echo 🚀 QPaper AI Setup - Cloud Databases + Local Storage
echo =====================================================

echo 📋 Step 1: Creating environment file...
if not exist "backend\.env" (
    copy "backend\env.example" "backend\.env"
    echo ✅ Created backend\.env from template
    echo.
    echo ⚠️  IMPORTANT: Edit backend\.env with your cloud database URLs
    echo    - Get Supabase URL: https://supabase.com
    echo    - Get MongoDB URL: https://cloud.mongodb.com  
    echo    - Get Redis URL: https://redis.com/redis-enterprise-cloud/
    echo.
    pause
) else (
    echo ⚠️  backend\.env already exists
)

echo.
echo 📋 Step 2: Creating storage directories...
if not exist "storage\papers" mkdir "storage\papers"
if not exist "storage\page_images" mkdir "storage\page_images"
if not exist "tmp\uploads" mkdir "tmp\uploads"
if not exist "logs" mkdir "logs"
echo ✅ Storage directories created

echo.
echo 📋 Step 3: Installing Python dependencies...
cd backend
pip install -r requirements.txt
echo ✅ Python dependencies installed

echo.
echo 📋 Step 4: Downloading spaCy model...
python -m spacy download en_core_web_sm
echo ✅ spaCy model downloaded

echo.
echo 📋 Step 5: Installing Node.js dependencies...
cd ..\frontend
npm install
echo ✅ Node.js dependencies installed

echo.
echo 📋 Step 6: Running database migration...
cd ..\backend
python migrate_to_cloud.py
echo ✅ Database migration completed

cd ..

echo.
echo ✅ Setup complete!
echo.
echo 📋 Next steps:
echo 1. Edit backend\.env with your cloud database URLs
echo 2. Start the application: docker-compose -f docker-compose.cloud.no-s3.yml up
echo 3. Access at: http://localhost:3000
echo 4. Login: admin/admin123 or student/student123
echo.
echo 🔧 For development without Docker:
echo - Backend: cd backend ^&^& uvicorn app.main:app --reload
echo - Frontend: cd frontend ^&^& npm run dev
echo - Celery: cd backend ^&^& celery -A app.tasks.celery worker --loglevel=info
echo.
echo 📚 See CLOUD_SETUP_NO_S3.md for detailed instructions
pause

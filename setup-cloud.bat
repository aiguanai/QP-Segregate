@echo off
echo 🚀 Setting up QPaper AI with Cloud Databases
echo ================================================

echo 📋 Step 1: Copying cloud environment file...
if not exist "backend\.env" (
    copy "env.cloud.example" "backend\.env"
    echo ✅ Created backend\.env from cloud template
    echo ⚠️  Please edit backend\.env with your cloud database URLs
) else (
    echo ⚠️  backend\.env already exists
)

echo.
echo 📋 Step 2: Installing Python dependencies...
cd backend
if exist "requirements.txt" (
    pip install -r requirements.txt
    echo ✅ Python dependencies installed
) else (
    echo ❌ requirements.txt not found
)

echo.
echo 📋 Step 3: Installing Node.js dependencies...
cd ..\frontend
if exist "package.json" (
    npm install
    echo ✅ Node.js dependencies installed
) else (
    echo ❌ package.json not found
)

echo.
echo 📋 Step 4: Downloading spaCy model...
cd ..\backend
python -m spacy download en_core_web_sm
echo ✅ spaCy model downloaded

echo.
echo 📋 Step 5: Creating directories...
cd ..
if not exist "storage\papers" mkdir "storage\papers"
if not exist "storage\page_images" mkdir "storage\page_images"
if not exist "tmp\uploads" mkdir "tmp\uploads"
if not exist "logs" mkdir "logs"
echo ✅ Directories created

echo.
echo 📋 Step 6: Running database migration...
cd backend
python migrate_to_cloud.py
echo ✅ Database migration completed

cd ..

echo.
echo ✅ Cloud setup complete!
echo.
echo 📋 Next steps:
echo 1. Edit backend\.env with your cloud database URLs
echo 2. Start the services: docker-compose -f docker-compose.cloud.yml up
echo 3. Access the application at http://localhost:3000
echo 4. Login with admin/admin123 or student/student123
echo.
echo 🔧 For development without Docker:
echo - Backend: cd backend ^&^& uvicorn app.main:app --reload
echo - Frontend: cd frontend ^&^& npm run dev
echo - Celery: cd backend ^&^& celery -A app.tasks.celery worker --loglevel=info
echo.
echo 📚 See CLOUD_SETUP.md for detailed cloud configuration instructions
pause

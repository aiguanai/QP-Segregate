@echo off
echo 🚀 Setting up QPaper AI - Automated Question Paper Management System

echo 📁 Creating directories...
if not exist "storage\papers" mkdir "storage\papers"
if not exist "storage\page_images" mkdir "storage\page_images"
if not exist "tmp\uploads" mkdir "tmp\uploads"
if not exist "logs" mkdir "logs"

echo 📋 Setting up environment files...
if not exist "backend\.env" (
    copy "backend\env.example" "backend\.env"
    echo ✅ Created backend\.env from template
) else (
    echo ⚠️  backend\.env already exists
)

if not exist "frontend\.env.local" (
    echo NEXT_PUBLIC_API_URL=http://localhost:8000 > "frontend\.env.local"
    echo ✅ Created frontend\.env.local
) else (
    echo ⚠️  frontend\.env.local already exists
)

echo 🐍 Installing Python dependencies...
cd backend
if exist "requirements.txt" (
    pip install -r requirements.txt
    echo ✅ Python dependencies installed
) else (
    echo ❌ requirements.txt not found
)
cd ..

echo 📦 Installing Node.js dependencies...
cd frontend
if exist "package.json" (
    npm install
    echo ✅ Node.js dependencies installed
) else (
    echo ❌ package.json not found
)
cd ..

echo 🧠 Downloading spaCy model...
python -m spacy download en_core_web_sm

echo ✅ Setup complete!
echo.
echo 📋 Next steps:
echo 1. Update backend\.env with your database credentials and API keys
echo 2. Start the services with: docker-compose up
echo 3. Access the application at http://localhost:3000
echo.
echo 🔧 For development:
echo - Backend: cd backend ^&^& uvicorn app.main:app --reload
echo - Frontend: cd frontend ^&^& npm run dev
echo - Celery: cd backend ^&^& celery -A app.tasks.celery worker --loglevel=info
echo.
echo 📚 Documentation: See README.md for detailed setup instructions
pause

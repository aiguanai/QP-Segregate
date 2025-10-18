#!/bin/bash

# QPaper AI Setup Script
echo "🚀 Setting up QPaper AI - Automated Question Paper Management System"

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p storage/papers
mkdir -p storage/page_images
mkdir -p tmp/uploads
mkdir -p logs

# Set permissions
echo "🔐 Setting permissions..."
chmod 755 storage
chmod 755 storage/papers
chmod 755 storage/page_images
chmod 755 tmp
chmod 755 tmp/uploads

# Copy environment files
echo "📋 Setting up environment files..."
if [ ! -f backend/.env ]; then
    cp backend/env.example backend/.env
    echo "✅ Created backend/.env from template"
else
    echo "⚠️  backend/.env already exists"
fi

if [ ! -f frontend/.env.local ]; then
    echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > frontend/.env.local
    echo "✅ Created frontend/.env.local"
else
    echo "⚠️  frontend/.env.local already exists"
fi

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
cd backend
if [ -f requirements.txt ]; then
    pip install -r requirements.txt
    echo "✅ Python dependencies installed"
else
    echo "❌ requirements.txt not found"
fi
cd ..

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
cd frontend
if [ -f package.json ]; then
    npm install
    echo "✅ Node.js dependencies installed"
else
    echo "❌ package.json not found"
fi
cd ..

# Download spaCy model
echo "🧠 Downloading spaCy model..."
python -m spacy download en_core_web_sm

echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Update backend/.env with your database credentials and API keys"
echo "2. Start the services with: docker-compose up"
echo "3. Access the application at http://localhost:3000"
echo ""
echo "🔧 For development:"
echo "- Backend: cd backend && uvicorn app.main:app --reload"
echo "- Frontend: cd frontend && npm run dev"
echo "- Celery: cd backend && celery -A app.tasks.celery worker --loglevel=info"
echo ""
echo "📚 Documentation: See README.md for detailed setup instructions"

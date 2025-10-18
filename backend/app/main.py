from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.api import admin, student, auth, courses
from app.core.config import settings
from app.core.database import engine
from app.models import Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="QPaper AI API",
    description="Automated Question Paper Management System",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for uploaded PDFs and images
if not os.path.exists("storage"):
    os.makedirs("storage")
if not os.path.exists("storage/papers"):
    os.makedirs("storage/papers")
if not os.path.exists("storage/page_images"):
    os.makedirs("storage/page_images")

app.mount("/storage", StaticFiles(directory="storage"), name="storage")

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(student.router, prefix="/api/student", tags=["Student"])
app.include_router(courses.router, prefix="/api/courses", tags=["Courses"])

@app.get("/")
async def root():
    return {"message": "QPaper AI API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

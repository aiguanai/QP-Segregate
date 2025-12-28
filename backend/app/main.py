from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import os
import traceback

from app.api import admin, student, auth, courses, public
# Don't import proposed_api at startup to avoid SQLAlchemy model conflicts
# It will be imported lazily if needed
PROPOSED_API_AVAILABLE = False
proposed_api = None
from app.core.config import settings
from app.core.database import engine
from app.models import Base

# Create database tables (if they don't exist)
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    # Tables might already exist, which is fine
    pass

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
# Proposed API disabled to avoid SQLAlchemy model conflicts
# Uncomment below if you need the proposed API endpoints
# try:
#     from app.api import proposed_api
#     app.include_router(proposed_api.router, prefix="/api/proposed", tags=["Proposed System"])
# except Exception as e:
#     print(f"⚠️  Proposed API not available: {e}")
app.include_router(public.router, prefix="/api/public", tags=["Public"])

@app.get("/")
async def root():
    print("🌐 Root endpoint accessed")
    return {"message": "QPaper AI API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

# Global exception handler to ensure CORS headers are always sent
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import sys
    sys.stderr.write(f"❌ Unhandled exception: {exc}\n")
    traceback.print_exc(file=sys.stderr)
    sys.stderr.flush()
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "type": type(exc).__name__},
        headers={
            "Access-Control-Allow-Origin": "http://localhost:3000",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

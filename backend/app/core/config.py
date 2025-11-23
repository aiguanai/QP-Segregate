from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database - Reads from .env file or environment variables
    # Priority: Environment variable > .env file > default
    DATABASE_URL: str = "postgresql://qpaper_user:qpaper_password@localhost:5432/qpaper_ai"
    MONGODB_URL: str = "mongodb://qpaper_user:qpaper_password@localhost:27017/qpaper_ai?authSource=admin"
    REDIS_URL: str = "redis://localhost:6379"
    
    # JWT
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # External APIs
    PINECONE_API_KEY: Optional[str] = None
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_S3_BUCKET: Optional[str] = None
    MATHPIX_API_KEY: Optional[str] = None
    
    # File Storage
    UPLOAD_DIR: str = "storage/papers"
    TEMP_UPLOAD_DIR: str = "tmp/uploads"
    PAGE_IMAGES_DIR: str = "storage/page_images"
    
    # Processing
    OCR_CONFIDENCE_THRESHOLD: float = 0.4
    CLASSIFICATION_CONFIDENCE_THRESHOLD: float = 0.7
    SIMILARITY_THRESHOLD: float = 0.85
    TEMP_UPLOAD_EXPIRE_HOURS: int = 24
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    class Config:
        env_file = ".env"

settings = Settings()

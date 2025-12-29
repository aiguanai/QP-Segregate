from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=True)  # Nullable for OAuth users (students)
    profile_picture_url = Column(String(500), nullable=True)  # Google profile picture URL
    display_name = Column(String(100), nullable=True)  # Display name from Google
    role = Column(String(20), nullable=False)  # ADMIN, STUDENT
    branch_id = Column(Integer, ForeignKey("branches.branch_id"), nullable=True)
    academic_year = Column(Integer, nullable=True)  # 1, 2, 3, 4
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    branch = relationship("Branch", back_populates="users")
    uploaded_papers = relationship("QuestionPaper", back_populates="uploader")
    bookmarks = relationship("StudentBookmark", back_populates="student")

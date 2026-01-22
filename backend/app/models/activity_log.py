from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class ActivityLog(Base):
    __tablename__ = "activity_logs"
    
    log_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    activity_type = Column(String(50), nullable=False)  # COURSE_CREATED, COURSE_UPDATED, COURSE_DELETED, PAPER_UPLOADED, REVIEW_RESOLVED, etc.
    entity_type = Column(String(50), nullable=True)  # course, question_paper, question, review
    entity_id = Column(String(100), nullable=True)  # ID of the affected entity
    description = Column(Text, nullable=False)  # Human-readable description
    activity_metadata = Column(JSON, nullable=True)  # Additional data (JSON) - renamed from 'metadata' to avoid SQLAlchemy conflict
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    user = relationship("User", back_populates="activity_logs")


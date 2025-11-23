from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Branch(Base):
    __tablename__ = "branches"
    
    branch_id = Column(Integer, primary_key=True, index=True)
    branch_name = Column(String(100), nullable=False, unique=True)
    branch_code = Column(String(10), nullable=False, unique=True)
    description = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    users = relationship("User", back_populates="branch")
    course_offerings = relationship("CourseOffering", back_populates="branch")


"""
Proposed Database Schema - Exact Implementation from Original Proposal
This file contains the exact database structure as specified in the original proposal.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Semester(Base):
    """
    SEMESTER table as proposed
    Primary Key: SemID
    Key Attributes: SemName
    Relationships: 1-to-N with SUBJECT
    """
    __tablename__ = "semesters"
    
    sem_id = Column(Integer, primary_key=True, index=True)
    sem_name = Column(String(100), nullable=False, unique=True)  # e.g., "Semester 1", "Semester 2"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    subjects = relationship("Subject", back_populates="semester")

class Subject(Base):
    """
    SUBJECT table as proposed
    Primary Key: SubID
    Key Attributes: SubName, SemID (FK)
    Relationships: 1-to-N with UNIT
    """
    __tablename__ = "subjects"
    
    sub_id = Column(Integer, primary_key=True, index=True)
    sub_name = Column(String(200), nullable=False)
    sem_id = Column(Integer, ForeignKey("semesters.sem_id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    semester = relationship("Semester", back_populates="subjects")
    units = relationship("Unit", back_populates="subject")

class Unit(Base):
    """
    UNIT table as proposed
    Primary Key: UnitID
    Key Attributes: UnitName, SubID (FK)
    Relationships: 1-to-N with QUESTION
    """
    __tablename__ = "units"
    
    unit_id = Column(Integer, primary_key=True, index=True)
    unit_name = Column(String(200), nullable=False)
    sub_id = Column(Integer, ForeignKey("subjects.sub_id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    subject = relationship("Subject", back_populates="units")
    questions = relationship("ProposedQuestion", back_populates="unit")

class QPaper(Base):
    """
    QPAPER table as proposed
    Primary Key: PaperID
    Key Attributes: PaperName, UploadDate, FileLink (to Drive/GitHub)
    Relationships: 1-to-N with QUESTION
    """
    __tablename__ = "qpapers"
    
    paper_id = Column(Integer, primary_key=True, index=True)
    paper_name = Column(String(200), nullable=False)
    upload_date = Column(DateTime, nullable=False, server_default=func.now())
    file_link = Column(String(500), nullable=True)  # Link to Drive/GitHub
    file_path = Column(String(500), nullable=True)  # Local storage path
    processing_status = Column(String(20), default="UPLOADED")  # UPLOADED, PROCESSING, COMPLETED, FAILED
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    questions = relationship("ProposedQuestion", back_populates="paper")

class ProposedQuestion(Base):
    """
    QUESTION table as proposed - Central Table
    Primary Key: QuesID
    Key Attributes: QuesText, UnitID (FK), PaperID (FK), AITag
    Relationships: Many-to-1 with others
    """
    __tablename__ = "proposed_questions"
    
    ques_id = Column(Integer, primary_key=True, index=True)
    ques_text = Column(Text, nullable=False)
    unit_id = Column(Integer, ForeignKey("units.unit_id"), nullable=True)
    paper_id = Column(Integer, ForeignKey("qpapers.paper_id"), nullable=False)
    ai_tag = Column(String(100), nullable=True)  # AI-generated classification tag
    confidence_score = Column(Float, nullable=True)  # AI classification confidence
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    unit = relationship("Unit", back_populates="questions")
    paper = relationship("QPaper", back_populates="questions")

# Export all models
__all__ = [
    "Semester",
    "Subject", 
    "Unit",
    "QPaper",
    "ProposedQuestion"
]

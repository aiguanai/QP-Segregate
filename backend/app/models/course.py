from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Course(Base):
    __tablename__ = "courses"
    
    course_code = Column(String(10), primary_key=True, index=True)
    course_name = Column(String(200), nullable=False)
    credits = Column(Integer, nullable=False)
    course_type = Column(String(20), nullable=False)  # CORE, ELECTIVE, LAB
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    offerings = relationship("CourseOffering", back_populates="course")
    units = relationship("CourseUnit", back_populates="course")
    primary_equivalences = relationship("CourseEquivalence", foreign_keys="CourseEquivalence.primary_course_code", back_populates="primary_course")
    equivalent_equivalences = relationship("CourseEquivalence", foreign_keys="CourseEquivalence.equivalent_course_code", back_populates="equivalent_course")
    papers = relationship("QuestionPaper", back_populates="course")
    questions = relationship("Question", back_populates="course")

class CourseOffering(Base):
    __tablename__ = "course_offerings"
    
    offering_id = Column(Integer, primary_key=True, index=True)
    course_code = Column(String(10), ForeignKey("courses.course_code"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.branch_id"), nullable=False)
    academic_year = Column(Integer, nullable=False)  # 1, 2, 3, 4
    semester_type = Column(String(10), nullable=False)  # ODD, EVEN
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    course = relationship("Course", back_populates="offerings")

class CourseEquivalence(Base):
    __tablename__ = "course_equivalence"
    
    equivalence_id = Column(Integer, primary_key=True, index=True)
    primary_course_code = Column(String(10), ForeignKey("courses.course_code"), nullable=False)
    equivalent_course_code = Column(String(10), ForeignKey("courses.course_code"), nullable=False)
    reason = Column(String(200), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    primary_course = relationship("Course", foreign_keys=[primary_course_code], back_populates="primary_equivalences")
    equivalent_course = relationship("Course", foreign_keys=[equivalent_course_code], back_populates="equivalent_equivalences")

class CourseUnit(Base):
    __tablename__ = "course_units"
    
    unit_id = Column(Integer, primary_key=True, index=True)
    course_code = Column(String(10), ForeignKey("courses.course_code"), nullable=False)
    unit_number = Column(Integer, nullable=False)
    unit_name = Column(String(200), nullable=False)
    topics = Column(Text, nullable=True)  # JSON string of topics
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    course = relationship("Course", back_populates="units")
    questions = relationship("Question", back_populates="unit")

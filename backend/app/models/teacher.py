"""
Teacher Models - Profile, Subject Assignments, Class Allocations
"""
from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, TIMESTAMP, text
from sqlalchemy.orm import relationship
from app.database import Base


class TeacherProfile(Base):
    """Extended profile for teachers."""
    __tablename__ = "teacher_profiles"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    employee_id = Column(String(50), unique=True, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    designation = Column(String(100), nullable=True)
    joining_date = Column(Date, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="teacher_profile")
    department = relationship("Department", back_populates="teacher_profiles")
    teacher_subjects = relationship("TeacherSubject", back_populates="teacher")
    class_allocations = relationship("ClassAllocation", back_populates="teacher")
    quizzes = relationship("Quiz", back_populates="teacher")
    assignments = relationship("Assignment", back_populates="teacher")
    chat_conversations = relationship("ChatConversation", back_populates="teacher")
    
    def __repr__(self):
        return f"<TeacherProfile(id={self.id}, employee_id={self.employee_id})>"


class TeacherSubject(Base):
    """Teacher-Subject assignments (by admin)."""
    __tablename__ = "teacher_subjects"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    teacher_id = Column(Integer, ForeignKey("teacher_profiles.id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    academic_year = Column(String(9), nullable=False)
    is_active = Column(Boolean, default=True)
    assigned_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    
    # Relationships
    teacher = relationship("TeacherProfile", back_populates="teacher_subjects")
    subject = relationship("Subject", back_populates="teacher_subjects")
    
    def __repr__(self):
        return f"<TeacherSubject(teacher_id={self.teacher_id}, subject_id={self.subject_id})>"


class ClassAllocation(Base):
    """Class allocations (teacher to degree+department+semester+subject)."""
    __tablename__ = "class_allocations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    teacher_id = Column(Integer, ForeignKey("teacher_profiles.id", ondelete="CASCADE"), nullable=False)
    degree_id = Column(Integer, ForeignKey("degrees.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    semester_id = Column(Integer, ForeignKey("semesters.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    academic_year = Column(String(9), nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    teacher = relationship("TeacherProfile", back_populates="class_allocations")
    degree = relationship("Degree", back_populates="class_allocations")
    department = relationship("Department", back_populates="class_allocations")
    semester = relationship("Semester", back_populates="class_allocations")
    subject = relationship("Subject", back_populates="class_allocations")
    notes = relationship("ClassNote", back_populates="class_allocation", cascade="all, delete-orphan")

    
    def __repr__(self):
        return f"<ClassAllocation(teacher_id={self.teacher_id}, subject_id={self.subject_id})>"


class ClassNote(Base):
    """Notes uploaded by teacher for a specific class allocation."""
    __tablename__ = "class_notes"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    class_allocation_id = Column(Integer, ForeignKey("class_allocations.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    file_url = Column(String(500), nullable=False)
    uploaded_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    
    # Relationships
    class_allocation = relationship("ClassAllocation", back_populates="notes")
    
    def __repr__(self):
        return f"<ClassNote(id={self.id}, title={self.title})>"


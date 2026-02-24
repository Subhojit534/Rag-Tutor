"""
Academic Models - Degree, Department, Semester, Subject
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, TIMESTAMP, text
from sqlalchemy.orm import relationship
from app.database import Base


class Degree(Base):
    """Degree programs (e.g., B.Tech, M.Tech, BCA, MCA)."""
    __tablename__ = "degrees"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    duration_years = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)  # Soft delete
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    
    # Relationships
    semesters = relationship("Semester", back_populates="degree")
    subjects = relationship("Subject", back_populates="degree")
    student_profiles = relationship("StudentProfile", back_populates="degree")
    class_allocations = relationship("ClassAllocation", back_populates="degree")
    
    def __repr__(self):
        return f"<Degree(id={self.id}, code={self.code}, name={self.name})>"


class Department(Base):
    """Academic departments (e.g., Computer Science, Electronics)."""
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)  # Soft delete
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    
    # Relationships
    subjects = relationship("Subject", back_populates="department")
    student_profiles = relationship("StudentProfile", back_populates="department")
    teacher_profiles = relationship("TeacherProfile", back_populates="department")
    class_allocations = relationship("ClassAllocation", back_populates="department")
    
    def __repr__(self):
        return f"<Department(id={self.id}, code={self.code}, name={self.name})>"


class Semester(Base):
    """Semesters linked to degrees."""
    __tablename__ = "semesters"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    number = Column(Integer, nullable=False)
    degree_id = Column(Integer, ForeignKey("degrees.id", ondelete="CASCADE"), nullable=False)
    is_active = Column(Boolean, default=True)  # Soft delete
    
    # Relationships
    degree = relationship("Degree", back_populates="semesters")
    subjects = relationship("Subject", back_populates="semester")
    student_profiles = relationship("StudentProfile", back_populates="current_semester")
    student_subjects = relationship("StudentSubject", back_populates="semester")
    semester_history = relationship("SemesterHistory", back_populates="semester")
    class_allocations = relationship("ClassAllocation", back_populates="semester")
    
    def __repr__(self):
        return f"<Semester(id={self.id}, number={self.number}, degree_id={self.degree_id})>"


class Subject(Base):
    """Subjects defined by admin for degree + department + semester."""
    __tablename__ = "subjects"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    credits = Column(Integer, default=3)
    degree_id = Column(Integer, ForeignKey("degrees.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    semester_id = Column(Integer, ForeignKey("semesters.id"), nullable=False, index=True)
    is_active = Column(Boolean, default=True)  # Soft delete
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    
    # Relationships
    degree = relationship("Degree", back_populates="subjects")
    department = relationship("Department", back_populates="subjects")
    semester = relationship("Semester", back_populates="subjects")
    teacher_subjects = relationship("TeacherSubject", back_populates="subject")
    student_subjects = relationship("StudentSubject", back_populates="subject")
    class_allocations = relationship("ClassAllocation", back_populates="subject")
    quizzes = relationship("Quiz", back_populates="subject")
    assignments = relationship("Assignment", back_populates="subject")
    pdf_documents = relationship("PDFDocument", back_populates="subject")
    ai_chat_sessions = relationship("AIChatSession", back_populates="subject")
    ai_doubt_logs = relationship("AIDoubtLog", back_populates="subject")
    weak_topics = relationship("WeakTopic", back_populates="subject")
    class_weak_topics = relationship("ClassWeakTopic", back_populates="subject")
    chat_conversations = relationship("ChatConversation", back_populates="subject")
    
    def __repr__(self):
        return f"<Subject(id={self.id}, code={self.code}, name={self.name})>"

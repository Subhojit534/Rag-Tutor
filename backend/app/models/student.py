"""
Student Models - Profile, Subject Mapping, Semester History
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, TIMESTAMP, text
from sqlalchemy.orm import relationship
from app.database import Base


class StudentProfile(Base):
    """Extended profile for students."""
    __tablename__ = "student_profiles"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    roll_number = Column(String(50), unique=True, nullable=False, index=True)
    degree_id = Column(Integer, ForeignKey("degrees.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    current_semester_id = Column(Integer, ForeignKey("semesters.id"), nullable=False)
    passout_year = Column(Integer, nullable=False)
    admission_year = Column(Integer, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="student_profile")
    degree = relationship("Degree", back_populates="student_profiles")
    department = relationship("Department", back_populates="student_profiles")
    current_semester = relationship("Semester", back_populates="student_profiles")
    student_subjects = relationship("StudentSubject", back_populates="student")
    semester_history = relationship("SemesterHistory", back_populates="student")
    quiz_attempts = relationship("QuizAttempt", back_populates="student")
    assignment_submissions = relationship("AssignmentSubmission", back_populates="student")
    chat_conversations = relationship("ChatConversation", back_populates="student")
    ai_chat_sessions = relationship("AIChatSession", back_populates="student")
    ai_doubt_logs = relationship("AIDoubtLog", back_populates="student")
    ai_rate_limit = relationship("AIRateLimit", back_populates="student", uselist=False)
    weak_topics = relationship("WeakTopic", back_populates="student")
    
    def __repr__(self):
        return f"<StudentProfile(id={self.id}, roll_number={self.roll_number})>"


class StudentSubject(Base):
    """Student-Subject mapping (auto-assigned based on semester)."""
    __tablename__ = "student_subjects"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    semester_id = Column(Integer, ForeignKey("semesters.id"), nullable=False)
    academic_year = Column(String(9), nullable=False)  # e.g., "2024-2025"
    is_current = Column(Boolean, default=True)
    assigned_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    
    # Relationships
    student = relationship("StudentProfile", back_populates="student_subjects")
    subject = relationship("Subject", back_populates="student_subjects")
    semester = relationship("Semester", back_populates="student_subjects")
    
    def __repr__(self):
        return f"<StudentSubject(student_id={self.student_id}, subject_id={self.subject_id})>"


class SemesterHistory(Base):
    """Archived semesters for students."""
    __tablename__ = "semester_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    semester_id = Column(Integer, ForeignKey("semesters.id"), nullable=False)
    academic_year = Column(String(9), nullable=False)
    completed_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    
    # Relationships
    student = relationship("StudentProfile", back_populates="semester_history")
    semester = relationship("Semester", back_populates="semester_history")
    
    def __repr__(self):
        return f"<SemesterHistory(student_id={self.student_id}, semester_id={self.semester_id})>"

"""
Assignment Models - Assignments and Submissions
Files stored on disk, paths in MySQL.
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Enum, ForeignKey, TIMESTAMP, text
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class SubmissionStatus(str, enum.Enum):
    SUBMITTED = "submitted"
    GRADED = "graded"
    LATE = "late"
    RESUBMIT = "resubmit"


class Assignment(Base):
    """Assignment posted by teacher."""
    __tablename__ = "assignments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teacher_profiles.id"), nullable=False)
    due_date = Column(DateTime, nullable=False)
    max_marks = Column(Integer, default=100)
    attachment_url = Column(String(500), nullable=True)  # File path on disk
    is_active = Column(Boolean, default=True)  # Soft delete
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    
    # Relationships
    subject = relationship("Subject", back_populates="assignments")
    teacher = relationship("TeacherProfile", back_populates="assignments")
    submissions = relationship("AssignmentSubmission", back_populates="assignment", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Assignment(id={self.id}, title={self.title})>"


class AssignmentSubmission(Base):
    """Student's assignment submission."""
    __tablename__ = "assignment_submissions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("student_profiles.id"), nullable=False)
    submission_url = Column(String(500), nullable=False)  # File path on disk
    submitted_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    marks_obtained = Column(Integer, nullable=True)
    feedback = Column(Text, nullable=True)
    status = Column(Enum(SubmissionStatus, values_callable=lambda x: [e.value for e in x]), default=SubmissionStatus.SUBMITTED)
    
    # Relationships
    assignment = relationship("Assignment", back_populates="submissions")
    student = relationship("StudentProfile", back_populates="assignment_submissions")
    
    def __repr__(self):
        return f"<AssignmentSubmission(id={self.id}, assignment_id={self.assignment_id})>"

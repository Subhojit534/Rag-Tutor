"""
Quiz Models - Quiz, Questions, Attempts, Responses
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Enum, ForeignKey, TIMESTAMP, text
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class CorrectOption(str, enum.Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"


class Quiz(Base):
    """Quiz created by teacher for a subject."""
    __tablename__ = "quizzes"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teacher_profiles.id"), nullable=False)
    duration_minutes = Column(Integer, default=30)
    total_marks = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)  # Soft delete
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    
    # Relationships
    subject = relationship("Subject", back_populates="quizzes")
    teacher = relationship("TeacherProfile", back_populates="quizzes")
    questions = relationship("QuizQuestion", back_populates="quiz", cascade="all, delete-orphan")
    attempts = relationship("QuizAttempt", back_populates="quiz", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Quiz(id={self.id}, title={self.title})>"


class QuizQuestion(Base):
    """MCQ questions for a quiz."""
    __tablename__ = "quiz_questions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    question_text = Column(Text, nullable=False)
    option_a = Column(String(500), nullable=False)
    option_b = Column(String(500), nullable=False)
    option_c = Column(String(500), nullable=False)
    option_d = Column(String(500), nullable=False)
    correct_option = Column(Enum(CorrectOption), nullable=False)
    marks = Column(Integer, default=1)
    explanation = Column(Text, nullable=True)
    
    # Relationships
    quiz = relationship("Quiz", back_populates="questions")
    responses = relationship("QuizResponse", back_populates="question")
    
    def __repr__(self):
        return f"<QuizQuestion(id={self.id}, quiz_id={self.quiz_id})>"


class QuizAttempt(Base):
    """Student's quiz attempt."""
    __tablename__ = "quiz_attempts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("student_profiles.id"), nullable=False)
    started_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    submitted_at = Column(TIMESTAMP, nullable=True)
    score = Column(Integer, default=0)
    total_questions = Column(Integer, nullable=False)
    correct_answers = Column(Integer, default=0)
    is_completed = Column(Boolean, default=False)
    
    # Relationships
    quiz = relationship("Quiz", back_populates="attempts")
    student = relationship("StudentProfile", back_populates="quiz_attempts")
    responses = relationship("QuizResponse", back_populates="attempt", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<QuizAttempt(id={self.id}, student_id={self.student_id}, quiz_id={self.quiz_id})>"


class QuizResponse(Base):
    """Individual response for each question in an attempt."""
    __tablename__ = "quiz_responses"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    attempt_id = Column(Integer, ForeignKey("quiz_attempts.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("quiz_questions.id"), nullable=False)
    selected_option = Column(Enum(CorrectOption), nullable=True)
    is_correct = Column(Boolean, default=False)
    
    # Relationships
    attempt = relationship("QuizAttempt", back_populates="responses")
    question = relationship("QuizQuestion", back_populates="responses")
    
    def __repr__(self):
        return f"<QuizResponse(id={self.id}, attempt_id={self.attempt_id})>"

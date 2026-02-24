"""
RAG Tutor - SQLAlchemy Models Package
"""
from app.models.user import User
from app.models.academic import Degree, Department, Semester, Subject
from app.models.student import StudentProfile, StudentSubject, SemesterHistory
from app.models.teacher import TeacherProfile, TeacherSubject, ClassAllocation
from app.models.quiz import Quiz, QuizQuestion, QuizAttempt, QuizResponse
from app.models.assignment import Assignment, AssignmentSubmission
from app.models.chat import ChatConversation, ChatMessage
from app.models.ai import PDFDocument, AIChatSession, AIChatMessage, AIDoubtLog, AIRateLimit
from app.models.analytics import WeakTopic, ClassWeakTopic
from app.models.system import AuditLog, SystemSetting

__all__ = [
    "User",
    "Degree", "Department", "Semester", "Subject",
    "StudentProfile", "StudentSubject", "SemesterHistory",
    "TeacherProfile", "TeacherSubject", "ClassAllocation",
    "Quiz", "QuizQuestion", "QuizAttempt", "QuizResponse",
    "Assignment", "AssignmentSubmission",
    "ChatConversation", "ChatMessage",
    "PDFDocument", "AIChatSession", "AIChatMessage", "AIDoubtLog", "AIRateLimit",
    "WeakTopic", "ClassWeakTopic",
    "AuditLog", "SystemSetting"
]

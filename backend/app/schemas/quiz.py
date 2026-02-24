"""
Quiz Schemas - Quiz, Questions, Attempts
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from app.models.quiz import CorrectOption


# ==========================================
# Quiz Question Schemas
# ==========================================

class QuizQuestionBase(BaseModel):
    """Base question schema."""
    question_text: str = Field(..., min_length=3)
    option_a: str = Field(..., min_length=1, max_length=500)
    option_b: str = Field(..., min_length=1, max_length=500)
    option_c: str = Field(..., min_length=1, max_length=500)
    option_d: str = Field(..., min_length=1, max_length=500)
    correct_option: CorrectOption
    marks: int = Field(1, ge=1)
    explanation: Optional[str] = None


class QuizQuestionCreate(QuizQuestionBase):
    """Question creation (used within quiz creation)."""
    pass


class QuizQuestionResponse(QuizQuestionBase):
    """Question response (for teacher view)."""
    id: int

    class Config:
        from_attributes = True


class QuizQuestionStudent(BaseModel):
    """Question for student (without correct answer)."""
    id: int
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    marks: int

    class Config:
        from_attributes = True


# ==========================================
# Quiz Schemas
# ==========================================

class QuizBase(BaseModel):
    """Base quiz schema."""
    title: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None
    subject_id: int
    duration_minutes: int = Field(30, ge=5, le=180)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class QuizCreate(QuizBase):
    """Quiz creation with questions."""
    questions: List[QuizQuestionCreate] = Field(..., min_length=1)


class QuizUpdate(BaseModel):
    """Quiz update schema."""
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, ge=5, le=180)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    is_active: Optional[bool] = None


class QuizResponse(QuizBase):
    """Quiz response (without questions)."""
    id: int
    teacher_id: int
    total_marks: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class QuizWithQuestions(QuizResponse):
    """Quiz with all questions (teacher view)."""
    questions: List[QuizQuestionResponse]


class QuizForStudent(BaseModel):
    """Quiz for student (without answers)."""
    id: int
    title: str
    description: Optional[str]
    subject_id: int
    duration_minutes: int
    total_marks: int
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    questions: List[QuizQuestionStudent]

    class Config:
        from_attributes = True


# ==========================================
# Quiz Attempt Schemas
# ==========================================

class QuizAnswerSubmit(BaseModel):
    """Single answer submission."""
    question_id: int
    selected_option: Optional[CorrectOption]


class QuizAttemptSubmit(BaseModel):
    """Complete quiz submission."""
    answers: List[QuizAnswerSubmit]


class QuizAttemptResponse(BaseModel):
    """Quiz attempt response."""
    id: int
    quiz_id: int
    student_id: int
    started_at: datetime
    submitted_at: Optional[datetime]
    score: int
    total_questions: int
    correct_answers: int
    is_completed: bool

    class Config:
        from_attributes = True


class QuizAttemptListResponse(QuizAttemptResponse):
    """Quiz attempt response for teacher list."""
    student_name: str
    student_roll: str



class QuizResultResponse(QuizAttemptResponse):
    """Quiz result with detailed feedback."""
    total_marks: int
    percentage: float
    responses: List["QuizResponseDetail"]


class QuizResponseDetail(BaseModel):
    """Detailed response for each question."""
    question_id: int
    question_text: str
    selected_option: Optional[CorrectOption]
    correct_option: CorrectOption
    is_correct: bool
    marks: int
    explanation: Optional[str]

    class Config:
        from_attributes = True


# Rebuild for forward reference
QuizResultResponse.model_rebuild()

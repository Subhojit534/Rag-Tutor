"""
Assignment Schemas - Assignments and Submissions
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.assignment import SubmissionStatus


# ==========================================
# Assignment Schemas
# ==========================================

class AssignmentBase(BaseModel):
    """Base assignment schema."""
    title: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None
    subject_id: int
    due_date: datetime
    max_marks: int = Field(100, ge=1, le=1000)


class AssignmentCreate(AssignmentBase):
    """Assignment creation schema."""
    pass


class AssignmentUpdate(BaseModel):
    """Assignment update schema."""
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    max_marks: Optional[int] = Field(None, ge=1, le=1000)
    is_active: Optional[bool] = None


class AssignmentResponse(AssignmentBase):
    """Assignment response schema."""
    id: int
    teacher_id: int
    attachment_url: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AssignmentWithSubmissionStatus(AssignmentResponse):
    """Assignment with student's submission status."""
    has_submitted: bool
    submission_status: Optional[SubmissionStatus]
    marks_obtained: Optional[int]


# ==========================================
# Submission Schemas
# ==========================================

class SubmissionResponse(BaseModel):
    """Assignment submission response."""
    id: int
    assignment_id: int
    student_id: int
    submission_url: str
    submitted_at: datetime
    marks_obtained: Optional[int]
    feedback: Optional[str]
    status: SubmissionStatus

    class Config:
        from_attributes = True


class SubmissionGrade(BaseModel):
    """Grading request for a submission."""
    marks_obtained: int = Field(..., ge=0)
    feedback: Optional[str] = None
    status: SubmissionStatus = SubmissionStatus.GRADED


class SubmissionWithStudent(SubmissionResponse):
    """Submission with student details (for teacher view)."""
    student_name: str
    student_roll: str

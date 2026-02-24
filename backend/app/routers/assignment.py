"""
Assignment Router - Assignment Management and Submissions
Files stored on disk, paths in MySQL.
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models.user import User
from app.models.student import StudentProfile, StudentSubject
from app.models.teacher import TeacherProfile
from app.models.academic import Subject
from app.models.assignment import Assignment, AssignmentSubmission, SubmissionStatus
from app.schemas.assignment import (
    AssignmentCreate, AssignmentUpdate, AssignmentResponse,
    SubmissionResponse, SubmissionGrade, SubmissionWithStudent
)
from app.utils.security import get_student_user, get_teacher_user
from app.utils.file_handler import save_assignment_attachment, save_assignment_submission


router = APIRouter(prefix="/api/assignments", tags=["Assignments"])


# ==========================================
# TEACHER ENDPOINTS
# ==========================================

@router.post("/", response_model=AssignmentResponse, status_code=201)
async def create_assignment(
    request: AssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_teacher_user)
):
    """Create a new assignment (teacher only)."""
    profile = db.query(TeacherProfile).filter(
        TeacherProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Teacher profile not found")
    
    assignment = Assignment(
        title=request.title,
        description=request.description,
        subject_id=request.subject_id,
        teacher_id=profile.id,
        due_date=request.due_date,
        max_marks=request.max_marks
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    
    return assignment


@router.post("/{assignment_id}/attachment")
async def upload_assignment_attachment(
    assignment_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_teacher_user)
):
    """Upload attachment for an assignment (teacher only)."""
    profile = db.query(TeacherProfile).filter(
        TeacherProfile.user_id == current_user.id
    ).first()
    
    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id,
        Assignment.teacher_id == profile.id
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Save file to disk, store path in MySQL
    file_path = await save_assignment_attachment(file, assignment_id)
    assignment.attachment_url = file_path
    
    db.commit()
    
    return {"message": "Attachment uploaded", "path": file_path}


@router.get("/teacher", response_model=List[AssignmentResponse])
async def get_teacher_assignments(
    subject_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_teacher_user)
):
    """Get assignments created by current teacher."""
    profile = db.query(TeacherProfile).filter(
        TeacherProfile.user_id == current_user.id
    ).first()
    
    query = db.query(Assignment).filter(Assignment.teacher_id == profile.id)
    
    if subject_id:
        query = query.filter(Assignment.subject_id == subject_id)
    
    return query.order_by(Assignment.created_at.desc()).all()


@router.get("/teacher/{assignment_id}/submissions")
async def get_assignment_submissions(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_teacher_user)
):
    """Get all submissions for an assignment (teacher only)."""
    profile = db.query(TeacherProfile).filter(
        TeacherProfile.user_id == current_user.id
    ).first()
    
    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id,
        Assignment.teacher_id == profile.id
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    submissions = db.query(AssignmentSubmission).options(
        joinedload(AssignmentSubmission.student).joinedload(StudentProfile.user)
    ).filter(AssignmentSubmission.assignment_id == assignment_id).all()
    
    return [
        {
            "id": s.id,
            "assignment_id": s.assignment_id,
            "student_id": s.student_id,
            "student_name": s.student.user.full_name,
            "student_roll": s.student.roll_number,
            "submission_url": s.submission_url,
            "submitted_at": s.submitted_at,
            "marks_obtained": s.marks_obtained,
            "feedback": s.feedback,
            "status": s.status
        }
        for s in submissions
    ]


@router.patch("/teacher/submissions/{submission_id}/grade")
async def grade_submission(
    submission_id: int,
    request: SubmissionGrade,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_teacher_user)
):
    """Grade a student's submission (teacher only)."""
    profile = db.query(TeacherProfile).filter(
        TeacherProfile.user_id == current_user.id
    ).first()
    
    submission = db.query(AssignmentSubmission).options(
        joinedload(AssignmentSubmission.assignment)
    ).filter(AssignmentSubmission.id == submission_id).first()
    
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    if submission.assignment.teacher_id != profile.id:
        raise HTTPException(status_code=403, detail="Not authorized to grade this submission")
    
    if request.marks_obtained > submission.assignment.max_marks:
        raise HTTPException(
            status_code=400, 
            detail=f"Marks cannot exceed maximum ({submission.assignment.max_marks})"
        )
    
    submission.marks_obtained = request.marks_obtained
    submission.feedback = request.feedback
    submission.status = request.status
    
    db.commit()
    
    return {"message": "Submission graded successfully"}


@router.patch("/teacher/{assignment_id}", response_model=AssignmentResponse)
async def update_assignment(
    assignment_id: int,
    request: AssignmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_teacher_user)
):
    """Update assignment (teacher only)."""
    profile = db.query(TeacherProfile).filter(
        TeacherProfile.user_id == current_user.id
    ).first()
    
    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id,
        Assignment.teacher_id == profile.id
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(assignment, key, value)
    
    db.commit()
    db.refresh(assignment)
    
    return assignment



@router.delete("/teacher/{assignment_id}", status_code=204)
async def delete_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_teacher_user)
):
    """Delete an assignment (teacher only)."""
    profile = db.query(TeacherProfile).filter(
        TeacherProfile.user_id == current_user.id
    ).first()
    
    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id,
        Assignment.teacher_id == profile.id
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    db.delete(assignment)
    db.commit()
    
    return None


# ==========================================
# STUDENT ENDPOINTS
# ==========================================

@router.get("/student")
async def get_student_assignments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_student_user)
):
    """Get assignments for current student with submission status."""
    profile = db.query(StudentProfile).filter(
        StudentProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    # Get student's current subjects
    subject_ids = [ss.subject_id for ss in db.query(StudentSubject).filter(
        StudentSubject.student_id == profile.id,
        StudentSubject.is_current == True
    ).all()]
    
    # Add implicit subjects (based on Semester + Degree + Department)
    # This ensures students see assignments for their current semester even if not explicitly enrolled
    implicit_subjects = db.query(Subject.id).filter(
        Subject.degree_id == profile.degree_id,
        Subject.department_id == profile.department_id,
        Subject.semester_id == profile.current_semester_id,
        Subject.is_active == True
    ).all()
    
    for s in implicit_subjects:
        if s.id not in subject_ids:
            subject_ids.append(s.id)
    
    # Get assignments
    assignments = db.query(Assignment).filter(
        Assignment.subject_id.in_(subject_ids),
        Assignment.is_active == True
    ).order_by(Assignment.due_date).all()
    
    result = []
    for assignment in assignments:
        submission = db.query(AssignmentSubmission).filter(
            AssignmentSubmission.assignment_id == assignment.id,
            AssignmentSubmission.student_id == profile.id
        ).first()
        
        result.append({
            "id": assignment.id,
            "title": assignment.title,
            "description": assignment.description,
            "subject_id": assignment.subject_id,
            "due_date": assignment.due_date,
            "max_marks": assignment.max_marks,
            "attachment_url": assignment.attachment_url,
            "is_overdue": assignment.due_date < datetime.utcnow(),
            "has_submitted": submission is not None,
            "submission_status": submission.status if submission else None,
            "marks_obtained": submission.marks_obtained if submission else None,
            "feedback": submission.feedback if submission else None
        })
    
    return result


@router.post("/student/{assignment_id}/submit")
async def submit_assignment(
    assignment_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_student_user)
):
    """Submit assignment (student only). File stored on disk, path in MySQL."""
    profile = db.query(StudentProfile).filter(
        StudentProfile.user_id == current_user.id
    ).first()
    
    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id,
        Assignment.is_active == True
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Check if already submitted
    existing = db.query(AssignmentSubmission).filter(
        AssignmentSubmission.assignment_id == assignment_id,
        AssignmentSubmission.student_id == profile.id
    ).first()
    
    if existing and existing.status != SubmissionStatus.RESUBMIT:
        raise HTTPException(status_code=400, detail="Already submitted. Resubmission not allowed.")
    
    # Save file to disk
    file_path = await save_assignment_submission(file, assignment_id, profile.id)
    
    # Check if late
    is_late = datetime.utcnow() > assignment.due_date
    status = SubmissionStatus.LATE if is_late else SubmissionStatus.SUBMITTED
    
    if existing:
        # Update existing submission
        existing.submission_url = file_path
        existing.submitted_at = datetime.utcnow()
        existing.status = status
        existing.marks_obtained = None
        existing.feedback = None
    else:
        # Create new submission
        submission = AssignmentSubmission(
            assignment_id=assignment_id,
            student_id=profile.id,
            submission_url=file_path,
            status=status
        )
        db.add(submission)
    
    db.commit()
    
    return {
        "message": "Assignment submitted successfully",
        "is_late": is_late,
        "file_path": file_path
    }


@router.get("/student/{assignment_id}")
async def get_assignment_detail(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_student_user)
):
    """Get detailed assignment info with submission status."""
    profile = db.query(StudentProfile).filter(
        StudentProfile.user_id == current_user.id
    ).first()
    
    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    submission = db.query(AssignmentSubmission).filter(
        AssignmentSubmission.assignment_id == assignment_id,
        AssignmentSubmission.student_id == profile.id
    ).first()
    
    return {
        "id": assignment.id,
        "title": assignment.title,
        "description": assignment.description,
        "subject_id": assignment.subject_id,
        "due_date": assignment.due_date,
        "max_marks": assignment.max_marks,
        "attachment_url": assignment.attachment_url,
        "created_at": assignment.created_at,
        "submission": {
            "id": submission.id,
            "submission_url": submission.submission_url,
            "submitted_at": submission.submitted_at,
            "status": submission.status,
            "marks_obtained": submission.marks_obtained,
            "feedback": submission.feedback
        } if submission else None
    }

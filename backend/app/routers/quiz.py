"""
Quiz Router - Quiz Management and Attempts
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from app.database import get_db
from app.models.user import User
from app.models.student import StudentProfile, StudentSubject
from app.models.teacher import TeacherProfile
from app.models.academic import Subject
from app.models.quiz import Quiz, QuizQuestion, QuizAttempt, QuizResponse
from app.schemas.quiz import (
    QuizCreate, QuizUpdate, QuizResponse as QuizResponseSchema,
    QuizWithQuestions, QuizForStudent,
    QuizAttemptSubmit, QuizAttemptResponse, QuizResultResponse, QuizResponseDetail,
    QuizQuestionCreate
)
from app.utils.security import get_student_user, get_teacher_user
from app.services.weak_topic_service import update_weak_topics_from_quiz


router = APIRouter(prefix="/api/quizzes", tags=["Quizzes"])


# ==========================================
# TEACHER ENDPOINTS
# ==========================================

@router.post("/", response_model=QuizResponseSchema, status_code=201)
async def create_quiz(
    request: QuizCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_teacher_user)
):
    """Create a new quiz with questions (teacher only)."""
    profile = db.query(TeacherProfile).filter(
        TeacherProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Teacher profile not found")
    
    # Calculate total marks
    total_marks = sum(q.marks for q in request.questions)
    
    # Create quiz
    quiz = Quiz(
        title=request.title,
        description=request.description,
        subject_id=request.subject_id,
        teacher_id=profile.id,
        duration_minutes=request.duration_minutes,
        total_marks=total_marks,
        start_time=request.start_time,
        end_time=request.end_time
    )
    db.add(quiz)
    db.flush()
    
    # Create questions
    for q in request.questions:
        question = QuizQuestion(
            quiz_id=quiz.id,
            question_text=q.question_text,
            option_a=q.option_a,
            option_b=q.option_b,
            option_c=q.option_c,
            option_d=q.option_d,
            correct_option=q.correct_option,
            marks=q.marks,
            explanation=q.explanation
        )
        db.add(question)
    
    db.commit()
    db.refresh(quiz)
    
    return quiz


@router.get("/teacher", response_model=List[QuizResponseSchema])
async def get_teacher_quizzes(
    subject_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_teacher_user)
):
    """Get quizzes created by current teacher."""
    profile = db.query(TeacherProfile).filter(
        TeacherProfile.user_id == current_user.id
    ).first()
    
    query = db.query(Quiz).filter(Quiz.teacher_id == profile.id)
    
    if subject_id:
        query = query.filter(Quiz.subject_id == subject_id)
    
    return query.order_by(Quiz.created_at.desc()).all()


@router.get("/teacher/{quiz_id}", response_model=QuizWithQuestions)
async def get_quiz_with_answers(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_teacher_user)
):
    """Get quiz with all questions and answers (teacher only)."""
    profile = db.query(TeacherProfile).filter(
        TeacherProfile.user_id == current_user.id
    ).first()
    
    quiz = db.query(Quiz).options(
        joinedload(Quiz.questions)
    ).filter(
        Quiz.id == quiz_id,
        Quiz.teacher_id == profile.id
    ).first()
    
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    return quiz


@router.patch("/teacher/{quiz_id}", response_model=QuizResponseSchema)
async def update_quiz(
    quiz_id: int,
    request: QuizUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_teacher_user)
):
    """Update quiz settings (teacher only)."""
    profile = db.query(TeacherProfile).filter(
        TeacherProfile.user_id == current_user.id
    ).first()
    
    quiz = db.query(Quiz).filter(
        Quiz.id == quiz_id,
        Quiz.teacher_id == profile.id
    ).first()
    
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(quiz, key, value)
    
    db.commit()
    db.refresh(quiz)
    
    return quiz


@router.get("/teacher/{quiz_id}/attempts")
async def get_quiz_attempts(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_teacher_user)
):
    """Get all attempts for a quiz (teacher only)."""
    profile = db.query(TeacherProfile).filter(
        TeacherProfile.user_id == current_user.id
    ).first()
    
    quiz = db.query(Quiz).filter(
        Quiz.id == quiz_id,
        Quiz.teacher_id == profile.id
    ).first()
    
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    attempts = db.query(QuizAttempt).options(
        joinedload(QuizAttempt.student).joinedload(StudentProfile.user)
    ).filter(QuizAttempt.quiz_id == quiz_id).all()
    
    return [
        {
            "id": a.id,
            "quiz_id": a.quiz_id,
            "student_id": a.student_id,
            "started_at": a.started_at,
            "submitted_at": a.submitted_at,
            "score": a.score,
            "total_questions": a.total_questions,
            "correct_answers": a.correct_answers,
            "is_completed": a.is_completed,
            "student_name": a.student.user.full_name,
            "student_roll": a.student.roll_number
        }
        for a in attempts
    ]




@router.post("/teacher/{quiz_id}/questions", response_model=QuizResponseSchema)
async def add_quiz_question(
    quiz_id: int,
    question: QuizQuestionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_teacher_user)
):
    """Add a question to an existing quiz."""
    profile = db.query(TeacherProfile).filter(
        TeacherProfile.user_id == current_user.id
    ).first()
    
    quiz = db.query(Quiz).filter(
        Quiz.id == quiz_id,
        Quiz.teacher_id == profile.id
    ).first()
    
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
        
    new_question = QuizQuestion(
        quiz_id=quiz.id,
        question_text=question.question_text,
        option_a=question.option_a,
        option_b=question.option_b,
        option_c=question.option_c,
        option_d=question.option_d,
        correct_option=question.correct_option,
        marks=question.marks,
        explanation=question.explanation
    )
    db.add(new_question)
    
    # Update total marks
    quiz.total_marks += question.marks
    
    db.commit()
    db.refresh(quiz)
    return quiz


@router.delete("/teacher/questions/{question_id}", status_code=204)
async def delete_quiz_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_teacher_user)
):
    """Delete a question from a quiz."""
    profile = db.query(TeacherProfile).filter(
        TeacherProfile.user_id == current_user.id
    ).first()
    
    # Verify ownership via quiz
    question = db.query(QuizQuestion).join(Quiz).filter(
        QuizQuestion.id == question_id,
        Quiz.teacher_id == profile.id
    ).first()
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    quiz = question.quiz
    quiz.total_marks -= question.marks
    
    db.delete(question)
    db.commit()
    return None


@router.delete("/teacher/{quiz_id}", status_code=204)
async def delete_quiz(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_teacher_user)
):
    """Delete a quiz (teacher only)."""
    profile = db.query(TeacherProfile).filter(
        TeacherProfile.user_id == current_user.id
    ).first()
    
    quiz = db.query(Quiz).filter(
        Quiz.id == quiz_id,
        Quiz.teacher_id == profile.id
    ).first()
    
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    db.delete(quiz)
    db.commit()
    
    return None


# ==========================================
# STUDENT ENDPOINTS
# ==========================================

@router.get("/student")
async def get_student_quizzes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_student_user)
):
    """Get available quizzes for current student."""
    profile = db.query(StudentProfile).filter(
        StudentProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    # Get student's current subjects (Explicit assignments)
    subject_ids = [ss.subject_id for ss in db.query(StudentSubject).filter(
        StudentSubject.student_id == profile.id,
        StudentSubject.is_current == True
    ).all()]
    
    # Add implicit subjects (based on Semester + Degree + Department)
    # This ensures students see quizzes for their current semester even if not explicitly enrolled
    implicit_subjects = db.query(Subject.id).filter(
        Subject.degree_id == profile.degree_id,
        Subject.department_id == profile.department_id,
        Subject.semester_id == profile.current_semester_id,
        Subject.is_active == True
    ).all()
    
    for s in implicit_subjects:
        if s.id not in subject_ids:
            subject_ids.append(s.id)
    
    # Get available quizzes
    now = datetime.utcnow()
    quizzes = db.query(Quiz).filter(
        Quiz.subject_id.in_(subject_ids),
        Quiz.is_active == True
    ).all()
    
    # Check attempt status for each quiz
    result = []
    for quiz in quizzes:
        attempt = db.query(QuizAttempt).filter(
            QuizAttempt.quiz_id == quiz.id,
            QuizAttempt.student_id == profile.id
        ).first()
        
        result.append({
            "id": quiz.id,
            "title": quiz.title,
            "description": quiz.description,
            "subject_id": quiz.subject_id,
            "duration_minutes": quiz.duration_minutes,
            "total_marks": quiz.total_marks,
            "start_time": quiz.start_time,
            "end_time": quiz.end_time,
            "is_attempted": attempt is not None,
            "is_completed": attempt.is_completed if attempt else False,
            "score": attempt.score if attempt and attempt.is_completed else None
        })
    
    return result


@router.get("/student/{quiz_id}/start")
async def start_quiz(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_student_user)
):
    """Start a quiz attempt and get questions (without answers)."""
    profile = db.query(StudentProfile).filter(
        StudentProfile.user_id == current_user.id
    ).first()
    
    quiz = db.query(Quiz).options(
        joinedload(Quiz.questions)
    ).filter(Quiz.id == quiz_id, Quiz.is_active == True).first()
    
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Check if already completed
    existing_attempt = db.query(QuizAttempt).filter(
        QuizAttempt.quiz_id == quiz_id,
        QuizAttempt.student_id == profile.id,
        QuizAttempt.is_completed == True
    ).first()
    
    if existing_attempt:
        raise HTTPException(status_code=400, detail="Quiz already completed")
    
    # Create or get attempt
    attempt = db.query(QuizAttempt).filter(
        QuizAttempt.quiz_id == quiz_id,
        QuizAttempt.student_id == profile.id
    ).first()
    
    if not attempt:
        attempt = QuizAttempt(
            quiz_id=quiz_id,
            student_id=profile.id,
            total_questions=len(quiz.questions)
        )
        db.add(attempt)
        db.commit()
        db.refresh(attempt)
    
    # Return quiz without correct answers
    return {
        "attempt_id": attempt.id,
        "quiz": {
            "id": quiz.id,
            "title": quiz.title,
            "description": quiz.description,
            "duration_minutes": quiz.duration_minutes,
            "total_marks": quiz.total_marks,
            "questions": [
                {
                    "id": q.id,
                    "question_text": q.question_text,
                    "option_a": q.option_a,
                    "option_b": q.option_b,
                    "option_c": q.option_c,
                    "option_d": q.option_d,
                    "marks": q.marks
                }
                for q in quiz.questions
            ]
        }
    }


@router.post("/student/{quiz_id}/submit")
async def submit_quiz(
    quiz_id: int,
    request: QuizAttemptSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_student_user)
):
    """Submit quiz answers and get instant evaluation."""
    profile = db.query(StudentProfile).filter(
        StudentProfile.user_id == current_user.id
    ).first()
    
    # Get attempt
    attempt = db.query(QuizAttempt).filter(
        QuizAttempt.quiz_id == quiz_id,
        QuizAttempt.student_id == profile.id,
        QuizAttempt.is_completed == False
    ).first()
    
    if not attempt:
        raise HTTPException(status_code=400, detail="No active attempt found")
    
    # Get questions
    questions = {q.id: q for q in db.query(QuizQuestion).filter(
        QuizQuestion.quiz_id == quiz_id
    ).all()}
    
    # Evaluate answers
    score = 0
    correct_count = 0
    wrong_topics = []
    
    for answer in request.answers:
        question = questions.get(answer.question_id)
        if not question:
            continue
        
        is_correct = answer.selected_option == question.correct_option
        if is_correct:
            score += question.marks
            correct_count += 1
        else:
            # Track wrong topic for weak topic detection
            wrong_topics.append({
                "question_id": question.id,
                "question_text": question.question_text[:100]
            })
        
        # Save response
        response = QuizResponse(
            attempt_id=attempt.id,
            question_id=answer.question_id,
            selected_option=answer.selected_option,
            is_correct=is_correct
        )
        db.add(response)
    
    # Update attempt
    attempt.is_completed = True
    attempt.submitted_at = datetime.utcnow()
    attempt.score = score
    attempt.correct_answers = correct_count
    
    db.commit()
    
    # Update weak topics based on wrong answers
    if wrong_topics:
        quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
        update_weak_topics_from_quiz(db, profile.id, quiz.subject_id, wrong_topics)
    
    return {
        "message": "Quiz submitted successfully",
        "score": score,
        "total_marks": attempt.quiz.total_marks,
        "correct_answers": correct_count,
        "total_questions": attempt.total_questions,
        "percentage": round((score / attempt.quiz.total_marks) * 100, 2) if attempt.quiz.total_marks > 0 else 0
    }


@router.get("/student/{quiz_id}/result")
async def get_quiz_result(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_student_user)
):
    """Get detailed quiz result with explanations."""
    profile = db.query(StudentProfile).filter(
        StudentProfile.user_id == current_user.id
    ).first()
    
    attempt = db.query(QuizAttempt).options(
        joinedload(QuizAttempt.responses)
    ).filter(
        QuizAttempt.quiz_id == quiz_id,
        QuizAttempt.student_id == profile.id,
        QuizAttempt.is_completed == True
    ).first()
    
    if not attempt:
        raise HTTPException(status_code=404, detail="No completed attempt found")
    
    questions = {q.id: q for q in db.query(QuizQuestion).filter(
        QuizQuestion.quiz_id == quiz_id
    ).all()}
    
    responses_detail = []
    for resp in attempt.responses:
        q = questions.get(resp.question_id)
        if q:
            responses_detail.append({
                "question_id": q.id,
                "question_text": q.question_text,
                "selected_option": resp.selected_option,
                "correct_option": q.correct_option,
                "is_correct": resp.is_correct,
                "marks": q.marks,
                "explanation": q.explanation
            })
    
    return {
        "quiz_id": quiz_id,
        "quiz_title": attempt.quiz.title,
        "score": attempt.score,
        "total_marks": attempt.quiz.total_marks,
        "correct_answers": attempt.correct_answers,
        "total_questions": attempt.total_questions,
        "percentage": round((attempt.score / attempt.quiz.total_marks) * 100, 2),
        "submitted_at": attempt.submitted_at,
        "responses": responses_detail
    }

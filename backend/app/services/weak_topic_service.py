"""
Weak Topic Service - Analyze and track student weak areas
"""
from typing import List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.analytics import WeakTopic, ClassWeakTopic, WeakTopicSource
from app.models.student import StudentProfile


def update_weak_topics_from_quiz(
    db: Session,
    student_id: int,
    subject_id: int,
    wrong_answers: List[Dict]
):
    """
    Update weak topics based on quiz wrong answers.
    
    Args:
        db: Database session
        student_id: Student profile ID
        subject_id: Subject ID
        wrong_answers: List of {"question_id": int, "question_text": str}
    """
    # Extract topics from wrong answers (simplified - use first few words as topic)
    for answer in wrong_answers:
        # Simple topic extraction - in production, use NLP
        topic_name = extract_topic(answer["question_text"])
        
        # Find or create weak topic
        weak_topic = db.query(WeakTopic).filter(
            WeakTopic.student_id == student_id,
            WeakTopic.subject_id == subject_id,
            WeakTopic.topic_name == topic_name
        ).first()
        
        if weak_topic:
            weak_topic.quiz_error_count += 1
            weak_topic.source = WeakTopicSource.COMBINED if weak_topic.ai_doubt_count > 0 else WeakTopicSource.QUIZ
            weak_topic.weakness_score = calculate_weakness_score(
                weak_topic.quiz_error_count,
                weak_topic.ai_doubt_count
            )
        else:
            weak_topic = WeakTopic(
                student_id=student_id,
                subject_id=subject_id,
                topic_name=topic_name,
                weakness_score=25.0,  # Initial score for first error
                source=WeakTopicSource.QUIZ,
                quiz_error_count=1,
                ai_doubt_count=0
            )
            db.add(weak_topic)
    
    db.commit()


def update_weak_topics_from_ai_doubt(
    db: Session,
    student_id: int,
    subject_id: int,
    topic: str
):
    """
    Update weak topics based on AI tutor doubt.
    """
    if not topic:
        return
    
    weak_topic = db.query(WeakTopic).filter(
        WeakTopic.student_id == student_id,
        WeakTopic.subject_id == subject_id,
        WeakTopic.topic_name == topic
    ).first()
    
    if weak_topic:
        weak_topic.ai_doubt_count += 1
        weak_topic.source = WeakTopicSource.COMBINED if weak_topic.quiz_error_count > 0 else WeakTopicSource.AI_DOUBTS
        weak_topic.weakness_score = calculate_weakness_score(
            weak_topic.quiz_error_count,
            weak_topic.ai_doubt_count
        )
    else:
        weak_topic = WeakTopic(
            student_id=student_id,
            subject_id=subject_id,
            topic_name=topic,
            weakness_score=15.0,  # Lower initial score for doubts
            source=WeakTopicSource.AI_DOUBTS,
            quiz_error_count=0,
            ai_doubt_count=1
        )
        db.add(weak_topic)
    
    db.commit()


def get_student_weak_topics(db: Session, student_id: int):
    """Get all weak topics for a student."""
    return db.query(WeakTopic).filter(
        WeakTopic.student_id == student_id
    ).order_by(WeakTopic.weakness_score.desc()).all()


def update_class_weak_topics(
    db: Session,
    degree_id: int,
    department_id: int,
    semester_id: int,
    subject_id: int
):
    """
    Aggregate weak topics for a class (for teacher analytics).
    """
    # Get all students in this class
    students = db.query(StudentProfile).filter(
        StudentProfile.degree_id == degree_id,
        StudentProfile.department_id == department_id,
        StudentProfile.current_semester_id == semester_id
    ).all()
    
    student_ids = [s.id for s in students]
    
    if not student_ids:
        return
    
    # Aggregate weak topics
    aggregated = db.query(
        WeakTopic.topic_name,
        func.count(WeakTopic.student_id).label('affected'),
        func.avg(WeakTopic.weakness_score).label('avg_score')
    ).filter(
        WeakTopic.student_id.in_(student_ids),
        WeakTopic.subject_id == subject_id
    ).group_by(WeakTopic.topic_name).all()
    
    for topic_name, affected, avg_score in aggregated:
        class_topic = db.query(ClassWeakTopic).filter(
            ClassWeakTopic.degree_id == degree_id,
            ClassWeakTopic.department_id == department_id,
            ClassWeakTopic.semester_id == semester_id,
            ClassWeakTopic.subject_id == subject_id,
            ClassWeakTopic.topic_name == topic_name
        ).first()
        
        if class_topic:
            class_topic.affected_students = affected
            class_topic.avg_weakness_score = avg_score
        else:
            class_topic = ClassWeakTopic(
                degree_id=degree_id,
                department_id=department_id,
                semester_id=semester_id,
                subject_id=subject_id,
                topic_name=topic_name,
                affected_students=affected,
                avg_weakness_score=avg_score
            )
            db.add(class_topic)
    
    db.commit()


def extract_topic(question_text: str) -> str:
    """
    Extract topic from question text.
    In production, use NLP/ML for better extraction.
    """
    # Simple extraction: use first 5 significant words
    words = question_text.split()[:10]
    # Remove common words
    stop_words = {'what', 'is', 'the', 'a', 'an', 'of', 'in', 'to', 'for', 'which', 'how'}
    significant = [w for w in words if w.lower() not in stop_words]
    return ' '.join(significant[:3]).title() if significant else "General"


def calculate_weakness_score(quiz_errors: int, ai_doubts: int) -> float:
    """
    Calculate weakness score (0-100).
    Quiz errors weighted more than doubts.
    """
    quiz_weight = 10  # Points per quiz error
    doubt_weight = 5  # Points per AI doubt
    
    score = (quiz_errors * quiz_weight) + (ai_doubts * doubt_weight)
    return min(100.0, score)  # Cap at 100

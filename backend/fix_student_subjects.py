import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.database import Base
from app.models.student import StudentProfile, StudentSubject
from app.models.academic import Subject

# Setup database connection
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def fix_student_subjects():
    print("Checking for students without subjects...")
    students = db.query(StudentProfile).all()
    count = 0
    
    for student in students:
        # Check if student already has subjects
        existing_count = db.query(StudentSubject).filter(
            StudentSubject.student_id == student.id,
            StudentSubject.is_current == True
        ).count()
        
        if existing_count == 0:
            print(f"Fixing subjects for student: {student.roll_number} (Sem {student.current_semester_id})")
            
            # Find subjects for this student's degree/dept/sem
            subjects = db.query(Subject).filter(
                Subject.degree_id == student.degree_id,
                Subject.department_id == student.department_id,
                Subject.semester_id == student.current_semester_id,
                Subject.is_active == True
            ).all()
            
            if not subjects:
                print(f"  - No subjects found for Degree {student.degree_id}, Dept {student.department_id}, Sem {student.current_semester_id}")
                continue
                
            for subject in subjects:
                print(f"  - Assigning: {subject.name} ({subject.code})")
                student_subject = StudentSubject(
                    student_id=student.id,
                    subject_id=subject.id,
                    semester_id=student.current_semester_id,
                    academic_year="2025-2026",
                    is_current=True
                )
                db.add(student_subject)
            
            count += 1
            
    db.commit()
    print(f"Done! Fixed subjects for {count} students.")

if __name__ == "__main__":
    fix_student_subjects()

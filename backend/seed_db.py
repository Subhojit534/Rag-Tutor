"""
Database Seeder - Populates initial data for Degrees, Departments, Semesters, and Subjects.
Run this script once to initialize the database with sample data.
"""
from sqlalchemy.orm import Session
from app.database import SessionLocal, init_db
from app.models.academic import Degree, Department, Semester, Subject

def seed_data(db: Session):
    print("🌱 Seeding database...")
    
    # 1. Degrees
    degrees = [
        {"name": "Bachelor of Technology", "code": "BTECH", "duration": 4},
        {"name": "Master of Technology", "code": "MTECH", "duration": 2},
        {"name": "Bachelor of Computer Applications", "code": "BCA", "duration": 3},
        {"name": "Master of Computer Applications", "code": "MCA", "duration": 2},
    ]
    
    db_degrees = {}
    for d in degrees:
        deg = db.query(Degree).filter(Degree.code == d["code"]).first()
        if not deg:
            deg = Degree(name=d["name"], code=d["code"], duration_years=d["duration"])
            db.add(deg)
            print(f"   Created Degree: {d['name']}")
        db_degrees[d["code"]] = deg
    db.commit()
    
    # Refresh to get IDs
    for code, deg in db_degrees.items():
        db.refresh(deg)

    # 2. Departments
    departments = [
        {"name": "Computer Science & Engineering", "code": "CSE"},
        {"name": "Electronics & Communication", "code": "ECE"},
        {"name": "Information Technology", "code": "IT"},
        {"name": "Artificial Intelligence & ML", "code": "AIML"},
    ]
    
    db_depts = {}
    for d in departments:
        dept = db.query(Department).filter(Department.code == d["code"]).first()
        if not dept:
            dept = Department(name=d["name"], code=d["code"])
            db.add(dept)
            print(f"   Created Department: {d['name']}")
        db_depts[d["code"]] = dept
    db.commit()
    
    # Refresh IDs
    for code, dept in db_depts.items():
        db.refresh(dept)

    # 3. Semesters (Create 8 semesters for BTECH)
    degree_btech = db_degrees["BTECH"]
    
    db_semesters = {}
    for i in range(1, 9):
        sem = db.query(Semester).filter(
            Semester.degree_id == degree_btech.id,
            Semester.number == i
        ).first()
        if not sem:
            sem = Semester(number=i, degree_id=degree_btech.id)
            db.add(sem)
            print(f"   Created Semester {i} for {degree_btech.code}")
        db_semesters[i] = sem
    db.commit()
    
    # Refresh IDs
    for i, sem in db_semesters.items():
        db.refresh(sem)

    # 4. Subjects (For BTECH CSE Semester 1)
    # We'll create a few sample subjects
    dept_cse = db_depts["CSE"]
    sem_1 = db_semesters[1]
    
    subjects = [
        {"name": "Engineering Mathematics I", "code": "MAT101", "credits": 4},
        {"name": "Programming in C", "code": "CS101", "credits": 4},
        {"name": "Digital Electronics", "code": "EC101", "credits": 3},
        {"name": "Communication Skills", "code": "ENG101", "credits": 2},
    ]
    
    for s in subjects:
        subj = db.query(Subject).filter(Subject.code == s["code"]).first()
        if not subj:
            subj = Subject(
                name=s["name"],
                code=s["code"],
                credits=s["credits"],
                degree_id=degree_btech.id,
                department_id=dept_cse.id,
                semester_id=sem_1.id
            )
            db.add(subj)
            print(f"   Created Subject: {s['name']}")
    
    db.commit()
    print("✅ Database seeding completed!")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_data(db)
    finally:
        db.close()

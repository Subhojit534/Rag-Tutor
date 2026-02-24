import sys
import os
import shutil
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add app to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base, get_db
from app.models.ai import PDFDocument
from app.config import settings

def check_db():
    print("--- Database Check ---")
    try:
        # Create a new session directly to avoid async/fastapi deps issues in script
        engine = create_engine(settings.DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        pdfs = db.query(PDFDocument).all()
        print(f"Total PDFs in DB: {len(pdfs)}")
        
        indexed = [p for p in pdfs if p.is_indexed]
        unindexed = [p for p in pdfs if not p.is_indexed]
        
        print(f"Indexed PDFs: {len(indexed)}")
        print(f"Unindexed PDFs: {len(unindexed)}")
        
        if unindexed:
            print("\nUnindexed PDFs details:")
            for p in unindexed:
                print(f" - ID: {p.id}, File: {p.file_name}, Subject: {p.subject_id}, Path: {p.file_path}")
                
        db.close()
    except Exception as e:
        print(f"DB Check Failed: {e}")

def check_tesseract():
    print("\n--- Tesseract Check ---")
    tesseract_cmd = shutil.which("tesseract")
    if tesseract_cmd:
        print(f"Tesseract found: {tesseract_cmd}")
    else:
        print("WARNING: Tesseract binary NOT found in PATH. OCR will fail.")
        
if __name__ == "__main__":
    check_db()
    check_tesseract()

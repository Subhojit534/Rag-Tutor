import sys
import os
import glob
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add app to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base
from app.models.ai import PDFDocument
from app.models.academic import Subject
from app.config import settings
from app.utils.pdf_ocr import extract_text_from_scanned_pdf
from app.ai.vector_store import get_vector_store
from app.routers.ai_tutor import extract_pdf_chunks

def reindex_all():
    print("--- Starting Global Re-indexing ---")
    
    # Connect
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    # 1. Scan filesystem for PDFs and ensure DB records exist
    uploads_dir = Path(settings.UPLOAD_DIR) / "class_notes"
    print(f"Scanning {uploads_dir}...")
    
    if uploads_dir.exists():
        # Look for subject folders: 1, 2, etc.
        for subject_dir in uploads_dir.iterdir():
            if subject_dir.is_dir() and subject_dir.name.isdigit():
                subject_id = int(subject_dir.name)
                print(f"Found Subject ID: {subject_id}")
                
                # Check if subject exists
                subject = db.query(Subject).get(subject_id)
                if not subject:
                    print(f"Skipping Subject {subject_id} (Not found in DB)")
                    continue
                
                # Scan files
                for file_path in subject_dir.glob("*.pdf"):
                    print(f"  Processing {file_path.name}...")
                    
                    # Check if exists in DB
                    # We store relative path usually, e.g. "class_notes/1/file.pdf"
                    # Or check by filename + subject_id
                    pdf_doc = db.query(PDFDocument).filter(
                        PDFDocument.subject_id == subject_id,
                        PDFDocument.file_name == file_path.name
                    ).first()
                    
                    if not pdf_doc:
                        print(f"  -> Creating DB record for {file_path.name}")
                        pdf_doc = PDFDocument(
                            subject_id=subject_id,
                            file_name=file_path.name,
                            file_path=str(file_path.relative_to(settings.UPLOAD_DIR)),
                            file_size=file_path.stat().st_size,
                            uploaded_by=1, # Default admin/system
                            is_indexed=False
                        )
                        db.add(pdf_doc)
                        db.commit()
                        db.refresh(pdf_doc)
                    
                    # Now Index it
                    try:
                        print(f"  -> Indexing...")
                        full_path = file_path
                        # Use our extractor with OCR fallback
                        chunks = extract_pdf_chunks(str(full_path), file_path.name)
                        
                        if chunks:
                            vector_store = get_vector_store(subject_id)
                            vector_store.add_documents(chunks)
                            
                            pdf_doc.is_indexed = True
                            db.commit()
                            print(f"  -> Success: {len(chunks)} chunks indexed.")
                        else:
                            print(f"  -> WARNING: No text extracted.")
                            
                    except Exception as e:
                        print(f"  -> FAILED: {e}")

    print("--- Re-indexing Complete ---")
    db.close()

if __name__ == "__main__":
    reindex_all()

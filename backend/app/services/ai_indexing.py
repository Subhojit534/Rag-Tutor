"""
AI Indexing Service - Shared logic for extracting and indexing PDFs.
"""
from typing import List, Dict, Optional
from datetime import datetime
from pypdf import PdfReader
from sqlalchemy.orm import Session
from app.models.ai import PDFDocument
from app.ai.vector_store import get_vector_store, reindex_subject
from app.utils.file_handler import get_full_path
from app.utils.pdf_ocr import extract_text_from_scanned_pdf


def extract_pdf_chunks(file_path: str, source_name: str, chunk_size: int = 500) -> List[dict]:
    """
    Extract text chunks from PDF for indexing.
    
    Args:
        file_path: Path to PDF file
        source_name: Source name for citation
        chunk_size: Target chunk size in characters
        
    Returns:
        List of {"text": str, "source": str, "page": int}
    """
    chunks = []
    
    try:
        reader = PdfReader(file_path)
        
        # Check if we got any reasonable text from the whole document
        full_text_check = "".join([page.extract_text() or "" for page in reader.pages])
        
        if len(full_text_check.strip()) < 100:
             # Likely a scanned PDF, try OCR on the whole file
             print(f"Detected scanned PDF: {source_name}, switching to OCR...")
             ocr_text = extract_text_from_scanned_pdf(file_path)
             
             if ocr_text:
                 # Clean and chunk the OCR text associated with page 1
                 text = ' '.join(ocr_text.split())
                 words = text.split()
                 current_chunk = []
                 current_length = 0
                 
                 for word in words:
                    current_chunk.append(word)
                    current_length += len(word) + 1
                    
                    if current_length >= chunk_size:
                        chunks.append({
                            "text": ' '.join(current_chunk),
                            "source": source_name,
                            "page": 1 
                        })
                        current_chunk = []
                        current_length = 0
                 
                 if current_chunk:
                    chunks.append({
                        "text": ' '.join(current_chunk),
                        "source": source_name,
                        "page": 1
                    })
                 return chunks

        # Standard Processing if text was found
        for page_num, page in enumerate(reader.pages, 1):
            text = page.extract_text()
            if not text:
                continue
            
            # Clean text
            text = ' '.join(text.split())
            
            # Split into chunks
            words = text.split()
            current_chunk = []
            current_length = 0
            
            for word in words:
                current_chunk.append(word)
                current_length += len(word) + 1
                
                if current_length >= chunk_size:
                    chunks.append({
                        "text": ' '.join(current_chunk),
                        "source": source_name,
                        "page": page_num
                    })
                    current_chunk = []
                    current_length = 0
            
            # Add remaining
            if current_chunk:
                chunks.append({
                    "text": ' '.join(current_chunk),
                    "source": source_name,
                    "page": page_num
                })
    
    except Exception as e:
        print(f"Error extracting PDF: {e}")
    
    return chunks


def index_pdf_document(db: Session, pdf_doc: PDFDocument) -> bool:
    """
    Index a PDFDocument into the vector store.
    Updates the is_indexed flag in the DB.
    """
    try:
        full_path = get_full_path(pdf_doc.file_path)
        if not full_path.exists():
            print(f"File not found for indexing: {full_path}")
            return False
            
        chunks = extract_pdf_chunks(str(full_path), pdf_doc.file_name)
        
        if not chunks:
            print(f"No chunks extracted from {pdf_doc.file_name}")
            return False
            
        vector_store = get_vector_store(pdf_doc.subject_id)
        vector_store.add_documents(chunks)
        
        pdf_doc.is_indexed = True
        pdf_doc.indexed_at = datetime.utcnow()
        db.commit()
        
        return True
        
    except Exception as e:
        print(f"Failed to index PDF {pdf_doc.id}: {e}")
        return False

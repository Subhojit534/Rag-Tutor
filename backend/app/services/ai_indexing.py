"""
AI Indexing Service - Shared logic for extracting and indexing PDFs.
"""
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.ai import PDFDocument
from app.ai.vector_store import get_vector_store, reindex_subject
from app.utils.file_handler import get_full_path


def extract_pdf_chunks(file_path: str, source_name: str, chunk_size: int = 500) -> List[dict]:
    """
    Extract text chunks from PDF for indexing.
    Uses PyMuPDF (fitz) which handles both text and scanned PDFs.
    
    Args:
        file_path: Path to PDF file
        source_name: Source name for citation
        chunk_size: Target chunk size in characters
        
    Returns:
        List of {"text": str, "source": str, "page": int}
    """
    chunks = []
    
    try:
        import fitz  # PyMuPDF
        
        doc = fitz.open(file_path)
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Extract text (works for both text-based and many scanned PDFs)
            text = page.get_text()
            
            # If no text found, try OCR via Tesseract (if available)
            if not text or len(text.strip()) < 20:
                try:
                    # Try to get text from page images using Tesseract
                    import pytesseract
                    from PIL import Image
                    import io
                    
                    # Render page to image at 300 DPI
                    pix = page.get_pixmap(dpi=200)
                    img_data = pix.tobytes("png")
                    img = Image.open(io.BytesIO(img_data))
                    
                    text = pytesseract.image_to_string(img)
                except Exception as ocr_err:
                    print(f"OCR failed for page {page_num + 1} of {source_name}: {ocr_err}")
                    continue
            
            if not text or len(text.strip()) < 10:
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
                        "page": page_num + 1
                    })
                    current_chunk = []
                    current_length = 0
            
            # Add remaining
            if current_chunk:
                chunks.append({
                    "text": ' '.join(current_chunk),
                    "source": source_name,
                    "page": page_num + 1
                })
        
        page_count = len(doc)
        doc.close()
        print(f"Extracted {len(chunks)} chunks from {source_name} ({page_count} pages)")
    
    except Exception as e:
        print(f"Error extracting PDF: {e}")
        import traceback
        traceback.print_exc()
    
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

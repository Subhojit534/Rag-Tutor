"""
OCR Utility for Scanned PDFs
Uses Tesseract and pdf2image to extract text from image-based PDFs.
"""
import pytesseract
from pdf2image import convert_from_path
import logging

# Configure logging
logger = logging.getLogger(__name__)

def extract_text_from_scanned_pdf(file_path: str) -> str:
    """
    Extract text from a scanned PDF using OCR.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Extracted text content
    """
    try:
        # Convert PDF to images
        images = convert_from_path(file_path)
        
        extracted_text = []
        
        for i, image in enumerate(images):
            # Perform OCR on each page
            text = pytesseract.image_to_string(image)
            extracted_text.append(text)
            
        return "\n".join(extracted_text)
        
    except Exception as e:
        logger.error(f"OCR Extraction failed for {file_path}: {str(e)}")
        # Return empty string or re-raise depending on strictness requirements
        # Returning empty string allows the caller to handle the 'no text found' case
        return ""

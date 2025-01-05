import PyPDF2
import io
import docx
import chardet
import pdfplumber
import traceback

def process_pdf(file_bytes):
    """Process PDF file and extract text, handling both normal and compressed PDFs."""
    text = ""
    
    # First try with PyPDF2
    try:
        print("Attempting to process PDF with PyPDF2...")
        pdf_file = io.BytesIO(file_bytes)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        # Extract text from all pages
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        if text.strip():  # If we got some text, return it
            return text.strip()
            
    except Exception as e:
        print(f"PyPDF2 processing failed: {str(e)}")
        print(traceback.format_exc())
    
    # If PyPDF2 fails or returns no text, try with pdfplumber
    try:
        print("Attempting to process PDF with pdfplumber...")
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        
        if text.strip():  # If we got some text, return it
            return text.strip()
            
    except Exception as e:
        print(f"pdfplumber processing failed: {str(e)}")
        print(traceback.format_exc())
    
    # If both methods fail, return None
    return None

def process_docx(file_bytes):
    """Process DOCX file and extract text."""
    try:
        print("Processing DOCX file...")
        doc = docx.Document(io.BytesIO(file_bytes))
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text.strip() if text.strip() else None
    except Exception as e:
        print(f"Error processing DOCX: {str(e)}")
        print(traceback.format_exc())
        return None

def process_txt(file_bytes):
    """Process TXT file and extract text, handling different encodings."""
    try:
        print("Processing TXT file...")
        # Detect encoding
        result = chardet.detect(file_bytes)
        encoding = result['encoding'] if result['encoding'] else 'utf-8'
        print(f"Detected encoding: {encoding}")
        
        # Try to decode with detected encoding
        try:
            text = file_bytes.decode(encoding)
            return text.strip() if text.strip() else None
        except UnicodeDecodeError:
            # Fallback to utf-8 if detected encoding fails
            print("Falling back to utf-8 encoding...")
            text = file_bytes.decode('utf-8', errors='ignore')
            return text.strip() if text.strip() else None
    except Exception as e:
        print(f"Error processing TXT: {str(e)}")
        print(traceback.format_exc())
        return None

def process_file(file_bytes, filename):
    """Process uploaded file based on its extension."""
    print(f"Processing file: {filename}")
    filename = filename.lower()
    
    if filename.endswith('.pdf'):
        return process_pdf(file_bytes)
    elif filename.endswith('.docx'):
        return process_docx(file_bytes)
    elif filename.endswith('.txt'):
        return process_txt(file_bytes)
    else:
        print(f"Unsupported file type: {filename}")
        return None

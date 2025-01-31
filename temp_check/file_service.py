import os
import magic
from docx import Document
from PyPDF2 import PdfReader
import logging
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {
    'application/pdf': '.pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
    'application/msword': '.doc',
    'text/plain': '.txt'
}

class FileService:
    def __init__(self, upload_folder):
        self.upload_folder = upload_folder
        os.makedirs(upload_folder, exist_ok=True)

    def allowed_file(self, file):
        """Check if file type is allowed"""
        mime = magic.from_buffer(file.read(2048), mime=True)
        file.seek(0)  # Reset file pointer
        return mime in ALLOWED_EXTENSIONS

    def save_file(self, file):
        """Save uploaded file and return the path"""
        if not file:
            raise ValueError("No file provided")

        if not self.allowed_file(file):
            raise ValueError("File type not allowed")

        filename = secure_filename(file.filename)
        file_path = os.path.join(self.upload_folder, filename)
        file.save(file_path)
        return file_path

    def extract_text(self, file_path):
        """Extract text from various file formats"""
        mime = magic.from_file(file_path, mime=True)

        if mime == 'application/pdf':
            return self._extract_from_pdf(file_path)
        elif mime in ['application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword']:
            return self._extract_from_docx(file_path)
        elif mime == 'text/plain':
            return self._extract_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {mime}")

    def _extract_from_pdf(self, file_path):
        """Extract text from PDF"""
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise

    def _extract_from_docx(self, file_path):
        """Extract text from DOCX"""
        try:
            doc = Document(file_path)
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            logger.error(f"Error extracting text from DOCX: {str(e)}")
            raise

    def _extract_from_txt(self, file_path):
        """Extract text from TXT"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            logger.error(f"Error extracting text from TXT: {str(e)}")
            raise

    def cleanup_file(self, file_path):
        """Remove temporary uploaded file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            logger.error(f"Error cleaning up file: {str(e)}")

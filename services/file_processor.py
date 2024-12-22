import docx
import PyPDF2

class FileProcessor:
    @staticmethod
    def extract_text(file_stream, filename: str) -> str:
        file_extension = filename.lower().split('.')[-1]
        
        if file_extension == 'pdf':
            return FileProcessor._extract_from_pdf(file_stream)
        elif file_extension in ['docx', 'doc']:
            return FileProcessor._extract_from_docx(file_stream)
        elif file_extension == 'tex':
            return file_stream.read().decode('utf-8')
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")

    @staticmethod
    def _extract_from_pdf(file_stream) -> str:
        pdf_reader = PyPDF2.PdfReader(file_stream)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text

    @staticmethod
    def _extract_from_docx(file_stream) -> str:
        doc = docx.Document(file_stream)
        return " ".join([paragraph.text for paragraph in doc.paragraphs])
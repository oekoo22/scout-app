import os
from PyPDF2 import PdfReader
from agents import function_tool

@function_tool
def read_local_pdf(file_path: str) -> str:
    """Read a PDF file from any local path and return its content as text."""
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found at path: {file_path}")
    
    if not file_path.lower().endswith('.pdf'):
        raise ValueError(f"File {file_path} is not a PDF file")
    
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        raise ValueError(f"Error reading PDF file: {str(e)}")
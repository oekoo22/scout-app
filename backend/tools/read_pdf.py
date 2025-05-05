import os
from PyPDF2 import PdfReader
from agents import function_tool

@function_tool
def read_pdf(filename: str) -> str:
    """Read a PDF file from the assets folder and return its content as text."""
    assets_dir = os.path.join(os.path.dirname(__file__), "../assets")
    file_path = os.path.join(assets_dir, filename)
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {filename} not found in assets folder")
    
    if not filename.lower().endswith('.pdf'):
        raise ValueError(f"File {filename} is not a PDF file")
    
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        raise ValueError(f"Error reading PDF file: {str(e)}")

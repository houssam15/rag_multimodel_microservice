from pathlib import Path

PDF_EXTENSIONS = {".pdf"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}
TEXT_EXTENSIONS = {".txt", ".md"}
DOC_EXTENSIONS = {".docx"}
PPT_EXTENSIONS = {".pptx"}
CSV_EXTENSIONS = {".csv"}

def get_file_type(filename:str) -> str | None:
    ext = Path(filename).suffix.lower()
    if ext in PDF_EXTENSIONS:
        return "pdf"
    if ext in IMAGE_EXTENSIONS:
        return "image"
    if ext in TEXT_EXTENSIONS:
        return "text"
    if ext in DOC_EXTENSIONS:
        return "docx"
    if ext in PPT_EXTENSIONS:
        return "pptx"
    if ext in CSV_EXTENSIONS:
        return "csv"    
    return None
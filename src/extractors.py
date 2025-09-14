# src/extractors.py
import docx2txt
import fitz  # PyMuPDF

def extract_text(file_path: str) -> str:
    """
    Extract text from PDF or DOCX file.
    """
    text = ""

    if file_path.endswith(".pdf"):
        doc = fitz.open(file_path)
        for page in doc:
            text += page.get_text()
        doc.close()

    elif file_path.endswith(".docx"):
        text = docx2txt.process(file_path)

    else:
        raise ValueError("Unsupported file format. Please upload PDF or DOCX.")

    return text.strip()

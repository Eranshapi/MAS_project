import os
from pptx import Presentation
import fitz  # PyMuPDF for PDFs
from docx import Document


def extract_text_from_docx(file_path):
    doc = Document(file_path)
    text = []
    for paragraph in doc.paragraphs:
        text.append(paragraph.text)
    return "\n".join(text)

def extract_text_from_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def extract_text_from_pptx(file_path):
    prs = Presentation(file_path)
    text = []
    for slide in prs.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                text.append(shape.text)
    return "\n".join(text)

def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    text = "\n".join([page.get_text("text") for page in doc])
    return text

def extract_text_from_folder(folder_path):
    """Extracts text from all .txt, .pptx, .pdf, and .docx files in a folder."""
    all_texts = []
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if file.endswith(".txt"):
            all_texts.append(extract_text_from_txt(file_path))
        elif file.endswith(".pptx"):
            all_texts.append(extract_text_from_pptx(file_path))
        elif file.endswith(".pdf"):
            all_texts.append(extract_text_from_pdf(file_path))
        elif file.endswith(".docx"):
            all_texts.append(extract_text_from_docx(file_path))
    return all_texts

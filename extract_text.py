import os
from typing import List, Dict
from pptx import Presentation
import fitz  # PyMuPDF
from docx import Document

def extract_text_from_docx(file_path: str) -> str:
    try:
        doc = Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs)
    except Exception as e:
        print(f"[ERROR] Failed to read DOCX '{file_path}': {e}")
        return ""

def extract_text_from_txt(file_path: str) -> str:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"[ERROR] Failed to read TXT '{file_path}': {e}")
        return ""

def extract_text_from_pptx(file_path: str) -> str:
    try:
        prs = Presentation(file_path)
        text = []
        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    text.append(shape.text)
        return "\n".join(text)
    except Exception as e:
        print(f"[ERROR] Failed to read PPTX '{file_path}': {e}")
        return ""

def extract_text_from_pdf(file_path: str) -> str:
    try:
        doc = fitz.open(file_path)
        return "\n".join(page.get_text("text") for page in doc)
    except Exception as e:
        print(f"[ERROR] Failed to read PDF '{file_path}': {e}")
        return ""

def extract_text_from_folder(folder_path: str) -> List[Dict[str, str]]:
    """
    Extracts text from supported files in a folder and returns a list of dictionaries:
    [{"filename": ..., "text": ...}, ...]
    """
    supported_exts = {".txt", ".pptx", ".pdf", ".docx"}
    extracted_docs = []

    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        ext = os.path.splitext(file)[1].lower()

        if ext not in supported_exts:
            print(f"[WARN] Skipping unsupported file type: {file}")
            continue

        if ext == ".txt":
            text = extract_text_from_txt(file_path)
        elif ext == ".pptx":
            text = extract_text_from_pptx(file_path)
        elif ext == ".pdf":
            text = extract_text_from_pdf(file_path)
        elif ext == ".docx":
            text = extract_text_from_docx(file_path)
        else:
            continue  # Should not reach here

        if text.strip():
            extracted_docs.append({"filename": file, "text": text})
        else:
            print(f"[INFO] Skipped empty or unreadable file: {file}")

    return extracted_docs

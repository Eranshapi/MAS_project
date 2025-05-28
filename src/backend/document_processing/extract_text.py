import os
from pptx import Presentation
import fitz  # PyMuPDF for PDFs
from docx import Document
import pytesseract
from pdf2image import convert_from_path
import logging
import tempfile
import sys
import shutil
import pdfplumber
import pandas as pd
from PIL import ImageEnhance

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configure Tesseract path for Windows
if os.name == 'nt':  # Windows
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def check_dependencies():
    """Check if all required dependencies are installed and accessible."""
    missing_deps = []
    
    # Check Tesseract
    try:
        tesseract_path = shutil.which('tesseract')
        if not tesseract_path:
            missing_deps.append("Tesseract OCR")
        else:
            # Configure Tesseract path
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
    except Exception as e:
        logger.error(f"Error checking Tesseract: {str(e)}")
        missing_deps.append("Tesseract OCR")

    # Check Poppler
    try:
        poppler_path = shutil.which('pdftoppm')
        if not poppler_path:
            missing_deps.append("Poppler")
    except Exception as e:
        logger.error(f"Error checking Poppler: {str(e)}")
        missing_deps.append("Poppler")

    if missing_deps:
        error_msg = "Missing required dependencies:\n"
        for dep in missing_deps:
            error_msg += f"- {dep}\n"
        error_msg += "\nPlease install the missing dependencies:\n"
        error_msg += "1. Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki\n"
        error_msg += "2. Poppler: https://github.com/oschwartz10612/poppler-windows/releases/\n"
        error_msg += "\nAfter installation, make sure to add them to your system PATH."
        logger.error(error_msg)
        return False
    return True

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

def create_searchable_chunks_view(text_content, output_file="chunks_view.txt"):
    """
    Creates a searchable view of the text chunks with clear separators and page numbers.
    """
    chunks = text_content.split("\n\n")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("SEARCHABLE CHUNKS VIEW\n")
        f.write("=" * 80 + "\n\n")
        
        for i, chunk in enumerate(chunks, 1):
            if chunk.strip():  # Only write non-empty chunks
                f.write(f"CHUNK {i}\n")
                f.write("-" * 40 + "\n")
                f.write(chunk.strip())
                f.write("\n\n")
                f.write("=" * 80 + "\n\n")

def extract_text_from_pdf(file_path):
    """
    Extract text from PDF files, handling both regular text and tables.
    Uses pdfplumber for better table extraction and PyMuPDF for regular text.
    Supports Hebrew text recognition.
    """
    if not check_dependencies():
        return ""

    try:
        text_content = []
        
        # First try with pdfplumber for better table handling
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                page_text = []
                
                # Extract tables
                tables = page.extract_tables()
                if tables:
                    print("Extracted tables:")
                    for i, table in enumerate(tables):
                        print(f"\nTable {i + 1}:")
                        for row in table:
                            print(row)
                else:
                    print("No tables found.")

                if tables:
                    for table in tables:
                        # Convert table to DataFrame for better handling
                        df = pd.DataFrame(table[1:], columns=table[0])
                        # Convert table to string with proper formatting
                        table_text = df.to_string(index=False)
                        page_text.append(f"\nTable:\n{table_text}\n")
                
                # Extract regular text
                page_text.append(page.extract_text() or "")
                
                # If no text is found, the page might be scanned
                if not any(text.strip() for text in page_text):
                    logger.info(f"Page {page_num + 1} appears to be scanned, using OCR...")
                    try:
                        with tempfile.TemporaryDirectory() as temp_dir:
                            # Convert PDF to image with higher DPI for better quality
                            images = convert_from_path(
                                file_path,
                                first_page=page_num + 1,
                                last_page=page_num + 1,
                                dpi=400,  # Increased DPI for better quality
                                output_folder=temp_dir
                            )
                            
                            if images:
                                # Preprocess the image for better OCR
                                img = images[0]
                                
                                # Convert to grayscale
                                img = img.convert('L')
                                
                                # Enhance contrast
                                enhancer = ImageEnhance.Contrast(img)
                                img = enhancer.enhance(2.0)  # Increase contrast
                                
                                # Try to detect tables first
                                try:
                                    # Use pytesseract to get table structure with better configuration
                                    table_data = pytesseract.image_to_data(
                                        img,
                                        lang='heb+eng',
                                        config='--psm 6 --oem 3',  # Use LSTM OCR Engine Mode
                                        output_type=pytesseract.Output.DICT
                                    )
                                    
                                    # Process the table data with improved algorithm
                                    if table_data['text']:
                                        # Group text by lines based on top position with improved tolerance
                                        lines = {}
                                        for i in range(len(table_data['text'])):
                                            if table_data['text'][i].strip():
                                                top = table_data['top'][i]
                                                left = table_data['left'][i]
                                                
                                                # Find the closest line within tolerance
                                                line_key = None
                                                min_diff = float('inf')
                                                for k in lines.keys():
                                                    if abs(k - top) < 15:  # Increased tolerance for line grouping
                                                        if abs(k - top) < min_diff:
                                                            min_diff = abs(k - top)
                                                            line_key = k
                                                
                                                if line_key is None:
                                                    line_key = top
                                                
                                                if line_key not in lines:
                                                    lines[line_key] = []
                                                
                                                # Sort items in line by left position
                                                lines[line_key].append((left, table_data['text'][i]))
                                        
                                        # Sort lines by top position
                                        sorted_lines = []
                                        for top in sorted(lines.keys()):
                                            # Sort items in line by left position
                                            sorted_items = [item[1] for item in sorted(lines[top], key=lambda x: x[0])]
                                            sorted_lines.append(sorted_items)
                                        
                                        # Convert to table format if we have multiple lines
                                        if len(sorted_lines) > 1:
                                            # Find the maximum number of columns
                                            max_cols = max(len(line) for line in sorted_lines)
                                            
                                            # Pad shorter lines with empty strings
                                            padded_lines = [line + [''] * (max_cols - len(line)) for line in sorted_lines]
                                            
                                            # Create DataFrame
                                            df = pd.DataFrame(padded_lines)
                                            
                                            # Clean up the table
                                            # Remove empty rows and columns
                                            df = df.replace('', pd.NA).dropna(how='all').dropna(axis=1, how='all')
                                            df = df.fillna('')
                                            
                                            # Convert to string with proper formatting
                                            table_text = df.to_string(index=False, header=False)
                                            page_text.append(f"\nTable from scanned image:\n{table_text}\n")
                                    
                                    # Add the regular OCR text with improved configuration
                                    ocr_text = pytesseract.image_to_string(
                                        img,
                                        lang='heb+eng',
                                        config='--psm 1 --oem 3'  # Use LSTM OCR Engine Mode
                                    )
                                    page_text.append(ocr_text)
                                except Exception as table_error:
                                    logger.error(f"Table detection failed for page {page_num + 1}: {str(table_error)}")
                                    # If table detection fails, just use the regular OCR text
                                    ocr_text = pytesseract.image_to_string(
                                        img,
                                        lang='heb+eng',
                                        config='--psm 1 --oem 3'
                                    )
                                    page_text.append(ocr_text)
                    except Exception as e:
                        logger.error(f"OCR failed for page {page_num + 1}: {str(e)}")
                        page_text = [""]
                
                text_content.append("\n".join(page_text))
        
        # Create a searchable view of the chunks
        create_searchable_chunks_view("\n\n".join(text_content))
        
        return "\n\n".join(text_content)
    
    except Exception as e:
        logger.error(f"Error extracting text from PDF {file_path}: {str(e)}")
        return ""

def extract_text_from_folder(folder_path):
    """Extracts text from all .txt, .pptx, .pdf, and .docx files in a folder and its subfolders."""
    all_texts = []
    
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith(".txt"):
                all_texts.append(extract_text_from_txt(file_path))
            elif file.endswith(".pptx"):
                all_texts.append(extract_text_from_pptx(file_path))
            elif file.endswith(".pdf"):
                all_texts.append(extract_text_from_pdf(file_path))
            elif file.endswith(".docx"):
                all_texts.append(extract_text_from_docx(file_path))
    return all_texts

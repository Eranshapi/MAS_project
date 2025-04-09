import re
from typing import List, Dict, Any

def preprocess_text(text: str) -> List[str]:
    """
    Preprocess text by cleaning and splitting it into paragraphs.
    
    Args:
        text: The input text to preprocess
        
    Returns:
        A list of paragraphs
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Split text into paragraphs (separated by double newlines or similar)
    paragraphs = re.split(r'\n\s*\n', text)
    
    # Clean paragraphs
    cleaned_paragraphs = []
    for para in paragraphs:
        para = para.strip()
        if para:  # Only keep non-empty paragraphs
            cleaned_paragraphs.append(para)
    
    return cleaned_paragraphs

def split_text_into_chunks(text_data, chunk_size=500, overlap=50):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)

    all_chunks = []
    for i, text in enumerate(text_data):
        cleaned = clean_text(text)
        chunks = text_splitter.create_documents([cleaned], metadatas=[{"source_doc": f"doc_{i}"}])
        all_chunks.extend(chunks)

    return all_chunks

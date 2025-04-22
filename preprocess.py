import re
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.document import Document


def clean_text(text):
    if not isinstance(text, str):  # Ensure input is a string
        print(f"Warning: Expected string, got {type(text)}")
        return ""  # Return empty string or handle as needed
    text = re.sub(r"\s+", " ", text).strip()  # Remove extra spaces
    return text


def preprocess_text(text: str) -> List[str]:
    """
    Splits cleaned text into paragraphs.
    """
    paragraphs = re.split(r'\n\s*\n', text)
    return [p.strip() for p in paragraphs if p.strip()]


def split_text_into_chunks(text_data, chunk_size=1000, overlap=150):
    """
    Splits the text data into chunks based on the given chunk size and overlap.

    Args:
        text_data: List of text documents to split.
        chunk_size: Maximum size of each chunk (in characters).
        overlap: Number of characters that overlap between adjacent chunks.

    Returns:
        all_chunks: List of chunks as Documents.
    """
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)

    all_chunks = []
    for i, text in enumerate(text_data):
        cleaned = clean_text(text)  # Clean text before chunking
        chunks = text_splitter.create_documents([cleaned], metadatas=[{"source_doc": f"doc_{i}"}])

        # Debugging: Print out the first 150 characters of each chunk for inspection
        print(f"Generated Chunks from document {i}:")
        for chunk in chunks:
            print(chunk.page_content[:150])  # Preview the first 150 characters of each chunk

        all_chunks.extend(chunks)

    return all_chunks

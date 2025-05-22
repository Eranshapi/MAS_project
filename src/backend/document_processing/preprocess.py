import re
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter


def clean_text(text):
    """Clean text while preserving table structure."""
    # Preserve table markers and structure
    if "Table:" in text:
        # Split into table and non-table parts
        parts = text.split("Table:")
        cleaned_parts = []
        
        for part in parts:
            if part.strip():
                if part.startswith("\n"):  # This is a table
                    # Clean table content while preserving structure
                    table_lines = part.strip().split("\n")
                    cleaned_lines = []
                    for line in table_lines:
                        # Clean each line while preserving alignment
                        cleaned_line = re.sub(r"\s+", " ", line).strip()
                        if cleaned_line:
                            cleaned_lines.append(cleaned_line)
                    cleaned_parts.append("Table:\n" + "\n".join(cleaned_lines))
                else:  # This is regular text
                    cleaned_parts.append(re.sub(r"\s+", " ", part).strip())
        
        return "\n".join(cleaned_parts)
    else:
        # Regular text cleaning
        return re.sub(r"\s+", " ", text).strip()


def preprocess_text(text: str) -> List[str]:
    """
    Preprocess text by cleaning and splitting it into paragraphs while preserving table structure.
    
    Args:
        text: The input text to preprocess
        
    Returns:
        A list of paragraphs
    """
    # Split text into paragraphs (separated by double newlines or similar)
    # But preserve table structure
    if "Table:" in text:
        # Split by table markers first
        parts = text.split("Table:")
        paragraphs = []
        
        for part in parts:
            if part.strip():
                if part.startswith("\n"):  # This is a table
                    paragraphs.append("Table:" + part)
                else:
                    # Split regular text into paragraphs
                    text_paragraphs = re.split(r'\n\s*\n', part)
                    paragraphs.extend([p.strip() for p in text_paragraphs if p.strip()])
    else:
        # Regular paragraph splitting
        paragraphs = re.split(r'\n\s*\n', text)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
    
    return paragraphs


def split_text_into_chunks(text_data, chunk_size=1000, overlap=200):
    """
    Split text into chunks while preserving table structure.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        length_function=len,
        separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
    )

    all_chunks = []
    for i, text in enumerate(text_data):
        # Clean the text while preserving table structure
        cleaned = clean_text(text)
        
        # If the text contains a table, handle it specially
        if "Table:" in cleaned:
            # Split by table markers
            parts = cleaned.split("Table:")
            current_chunk = []
            
            for part in parts:
                if part.strip():
                    if part.startswith("\n"):  # This is a table
                        # Keep the table as a single chunk
                        table_text = "Table:" + part
                        if current_chunk:
                            # Add any accumulated text before the table
                            chunks = text_splitter.create_documents(
                                ["\n".join(current_chunk)],
                                metadatas=[{"source_doc": f"doc_{i}"}]
                            )
                            all_chunks.extend(chunks)
                            current_chunk = []
                        
                        # Add the table as its own chunk
                        all_chunks.extend(text_splitter.create_documents(
                            [table_text],
                            metadatas=[{"source_doc": f"doc_{i}"}]
                        ))
                    else:
                        # Regular text - accumulate it
                        current_chunk.append(part)
            
            # Add any remaining text
            if current_chunk:
                chunks = text_splitter.create_documents(
                    ["\n".join(current_chunk)],
                    metadatas=[{"source_doc": f"doc_{i}"}]
                )
                all_chunks.extend(chunks)
        else:
            # Regular text splitting
            chunks = text_splitter.create_documents(
                [cleaned],
                metadatas=[{"source_doc": f"doc_{i}"}]
            )
            all_chunks.extend(chunks)

    return all_chunks

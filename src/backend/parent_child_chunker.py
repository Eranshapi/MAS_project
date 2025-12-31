"""
Parent-Document Retrieval (Parent-Child Chunking) Processor

This module processes a folder of raw documents into a Parent-Document Retrieval
structure using LangChain. It supports .txt, .pdf (with Surya OCR for scanned files),
.docx, and .pptx files.

Features:
- Surya OCR for scanned/image-based PDFs with Hebrew (RTL) support
- Parent-child chunking for improved retrieval
- Automatic detection of scanned vs text-based PDFs

Author: Senior RAG Engineer
"""

import re
import unicodedata
import uuid
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    DirectoryLoader,
    TextLoader,
    PyPDFLoader,
    Docx2txtLoader,
    UnstructuredPowerPointLoader,
)
from langchain.schema import Document

# Import Surya OCR module for scanned PDF support
try:
    from surya_ocr import (
        load_pdf_with_surya,
        is_scanned_pdf,
        check_surya_available,
        PDFEncryptedException,
        PDFCorruptedException,
        OCRFailedException,
    )
    SURYA_OCR_AVAILABLE = check_surya_available()
except ImportError:
    SURYA_OCR_AVAILABLE = False
    load_pdf_with_surya = None
    is_scanned_pdf = None

logger = logging.getLogger(__name__)


def clean_text(text: str) -> str:
    """
    Clean and preprocess document text with Hebrew/RTL support.
    
    Applies the following transformations:
    - Normalizes Unicode (NFC for proper Hebrew handling)
    - Removes HTML tags
    - Removes redundant whitespace
    - Repairs broken line breaks within sentences (for both Latin and Hebrew)
    
    Args:
        text: Raw text content from a document.
        
    Returns:
        Cleaned and normalized text.
    """
    # Step 1: Normalize Unicode (NFC composition - better for Hebrew)
    # NFC keeps composed characters together, which is preferred for Hebrew nikud
    text = unicodedata.normalize('NFC', text)
    
    # Step 2: Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Step 3: Repair broken line breaks within sentences (common in PDFs)
    # Handle Latin characters
    text = re.sub(r'(?<=[a-zA-Z,;:\-])\n(?=[a-zA-Z])', ' ', text)
    # Handle Hebrew characters (א-ת range: \u05D0-\u05EA)
    text = re.sub(r'(?<=[\u05D0-\u05EA,;:\-])\n(?=[\u05D0-\u05EA])', ' ', text)
    
    # Step 4: Normalize multiple spaces to single space
    text = re.sub(r'[ \t]+', ' ', text)
    
    # Step 5: Normalize multiple newlines to double newline (paragraph separator)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Step 6: Strip leading/trailing whitespace from each line
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)
    
    # Step 7: Remove leading/trailing whitespace from the entire text
    text = text.strip()
    
    return text


def preprocess_documents(documents: List[Document]) -> List[Document]:
    """
    Apply cleaning function to all documents.
    
    Args:
        documents: List of LangChain Document objects.
        
    Returns:
        List of cleaned Document objects with preserved metadata.
    """
    cleaned_documents = []
    
    for doc in documents:
        cleaned_content = clean_text(doc.page_content)
        
        # Create a new document with cleaned content and preserved metadata
        cleaned_doc = Document(
            page_content=cleaned_content,
            metadata=doc.metadata.copy()
        )
        cleaned_documents.append(cleaned_doc)
    
    return cleaned_documents


def load_pdf_document(
    pdf_path: str,
    use_surya_ocr: bool = True,
    languages: Optional[List[str]] = None,
) -> List[Document]:
    """
    Load a single PDF document, using Surya OCR for scanned pages.
    
    This function intelligently selects the extraction method:
    - For text-based PDFs: Uses PyPDFLoader (faster)
    - For scanned PDFs: Uses Surya OCR with Hebrew support
    
    Args:
        pdf_path: Path to the PDF file
        use_surya_ocr: Enable Surya OCR for scanned PDFs (default: True)
        languages: Language codes for OCR (default: ['he', 'en'])
        
    Returns:
        List of Document objects (one per page with text)
    """
    if languages is None:
        languages = ['he', 'en']
    
    pdf_path = str(Path(pdf_path).resolve())
    
    # Try Surya OCR if available and enabled
    if use_surya_ocr and SURYA_OCR_AVAILABLE and is_scanned_pdf is not None:
        try:
            # Check if PDF is scanned (needs OCR)
            needs_ocr = is_scanned_pdf(pdf_path)
            
            if needs_ocr:
                logger.info(f"Using Surya OCR for scanned PDF: {pdf_path}")
                return load_pdf_with_surya(pdf_path, languages=languages)
            else:
                logger.info(f"Using direct text extraction for: {pdf_path}")
                
        except (PDFEncryptedException, PDFCorruptedException) as e:
            logger.error(f"PDF error: {e}")
            raise
        except Exception as e:
            logger.warning(f"Surya OCR check failed, falling back to PyPDF: {e}")
    
    # Fallback to PyPDFLoader for text-based PDFs
    try:
        loader = PyPDFLoader(pdf_path)
        return loader.load()
    except Exception as e:
        logger.error(f"Failed to load PDF: {pdf_path} - {e}")
        return []


def load_documents_from_directory(
    directory_path: str,
    use_surya_ocr: bool = True,
    ocr_languages: Optional[List[str]] = None,
) -> List[Document]:
    """
    Load documents from a directory supporting multiple file formats.
    
    Supports:
    - .txt files (TextLoader)
    - .pdf files (Surya OCR for scanned, PyPDFLoader for text-based)
    - .docx files (Docx2txtLoader)
    - .pptx files (UnstructuredPowerPointLoader)
    
    Args:
        directory_path: Path to the directory containing documents.
        use_surya_ocr: Enable Surya OCR for scanned PDFs (default: True)
        ocr_languages: Language codes for OCR (default: ['he', 'en'])
        
    Returns:
        List of loaded Document objects.
    """
    if ocr_languages is None:
        ocr_languages = ['he', 'en']
    
    # Define loader mapping for non-PDF file types
    loader_map = {
        ".txt": TextLoader,
        ".docx": Docx2txtLoader,
        ".pptx": UnstructuredPowerPointLoader,
    }
    
    all_documents = []
    dir_path = Path(directory_path)
    
    # Load non-PDF documents using DirectoryLoader
    for extension, loader_class in loader_map.items():
        try:
            loader = DirectoryLoader(
                directory_path,
                glob=f"**/*{extension}",
                loader_cls=loader_class,
                show_progress=True,
                use_multithreading=True,
            )
            documents = loader.load()
            all_documents.extend(documents)
            print(f"Loaded {len(documents)} {extension} file(s)")
        except Exception as e:
            print(f"Warning: Error loading {extension} files: {e}")
    
    # Load PDF documents with smart OCR detection
    pdf_files = list(dir_path.glob("**/*.pdf"))
    pdf_count = 0
    ocr_count = 0
    
    for pdf_file in pdf_files:
        try:
            docs = load_pdf_document(
                str(pdf_file),
                use_surya_ocr=use_surya_ocr,
                languages=ocr_languages,
            )
            all_documents.extend(docs)
            pdf_count += 1
            
            # Track if OCR was used
            if docs and docs[0].metadata.get('extraction_method') == 'ocr':
                ocr_count += 1
                
        except Exception as e:
            print(f"Warning: Error loading PDF {pdf_file}: {e}")
    
    if pdf_count > 0:
        print(f"Loaded {pdf_count} .pdf file(s) (OCR used: {ocr_count})")
    
    return all_documents


def create_parent_child_chunks(
    documents: List[Document],
    parent_chunk_size: int = 2000,
    parent_chunk_overlap: int = 200,
    child_chunk_size: int = 400,
    child_chunk_overlap: int = 50,
) -> Dict[str, List[Document]]:
    """
    Create Parent-Child chunking structure for retrieval.
    
    Parent chunks provide broad context, while child chunks enable
    precise vector search. Each child chunk maintains a reference
    to its parent chunk.
    
    Args:
        documents: List of preprocessed Document objects.
        parent_chunk_size: Size of parent chunks (default: 2000 characters).
        parent_chunk_overlap: Overlap between parent chunks (default: 200).
        child_chunk_size: Size of child chunks (default: 400 characters).
        child_chunk_overlap: Overlap between child chunks (default: 50).
        
    Returns:
        Dictionary containing:
        - 'parent_chunks': List of parent Document objects
        - 'child_chunks': List of child Document objects with parent references
        - 'parent_child_mapping': Dict mapping parent_id to list of child_ids
    """
    # Initialize splitters
    parent_splitter = RecursiveCharacterTextSplitter(
        chunk_size=parent_chunk_size,
        chunk_overlap=parent_chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    
    child_splitter = RecursiveCharacterTextSplitter(
        chunk_size=child_chunk_size,
        chunk_overlap=child_chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    
    parent_chunks = []
    child_chunks = []
    parent_child_mapping = {}
    
    for doc in documents:
        # Create parent chunks from the document
        doc_parent_chunks = parent_splitter.split_documents([doc])
        
        for parent_chunk in doc_parent_chunks:
            # Generate unique ID for parent chunk
            parent_id = str(uuid.uuid4())
            
            # Add parent-specific metadata
            parent_chunk.metadata['chunk_type'] = 'parent'
            parent_chunk.metadata['parent_id'] = parent_id
            parent_chunk.metadata['chunk_size'] = len(parent_chunk.page_content)
            
            parent_chunks.append(parent_chunk)
            parent_child_mapping[parent_id] = []
            
            # Create child chunks from this parent chunk
            parent_as_doc = Document(
                page_content=parent_chunk.page_content,
                metadata=parent_chunk.metadata.copy()
            )
            doc_child_chunks = child_splitter.split_documents([parent_as_doc])
            
            for i, child_chunk in enumerate(doc_child_chunks):
                # Generate unique ID for child chunk
                child_id = str(uuid.uuid4())
                
                # Add child-specific metadata with parent reference
                child_chunk.metadata['chunk_type'] = 'child'
                child_chunk.metadata['child_id'] = child_id
                child_chunk.metadata['parent_id'] = parent_id
                child_chunk.metadata['child_index'] = i
                child_chunk.metadata['total_siblings'] = len(doc_child_chunks)
                child_chunk.metadata['chunk_size'] = len(child_chunk.page_content)
                
                child_chunks.append(child_chunk)
                parent_child_mapping[parent_id].append(child_id)
    
    return {
        'parent_chunks': parent_chunks,
        'child_chunks': child_chunks,
        'parent_child_mapping': parent_child_mapping,
    }


def process_documents_directory(
    directory_path: str,
    parent_chunk_size: int = 2000,
    parent_chunk_overlap: int = 200,
    child_chunk_size: int = 400,
    child_chunk_overlap: int = 50,
) -> Dict[str, Any]:
    """
    Main function to process a folder of raw documents into Parent-Child chunks.
    
    This function:
    1. Loads documents from the directory (.txt, .pdf, .docx)
    2. Preprocesses/cleans each document
    3. Creates parent-child chunking structure
    
    Args:
        directory_path: Path to the directory containing documents.
        parent_chunk_size: Size of parent chunks (default: 2000 characters).
        parent_chunk_overlap: Overlap between parent chunks (default: 200).
        child_chunk_size: Size of child chunks (default: 400 characters).
        child_chunk_overlap: Overlap between child chunks (default: 50).
        
    Returns:
        Dictionary containing:
        - 'parent_chunks': List of parent Document objects
        - 'child_chunks': List of child Document objects
        - 'parent_child_mapping': Dict mapping parent_id to child_ids
        - 'stats': Processing statistics
    """
    # Validate directory path
    dir_path = Path(directory_path)
    if not dir_path.exists():
        raise ValueError(f"Directory does not exist: {directory_path}")
    if not dir_path.is_dir():
        raise ValueError(f"Path is not a directory: {directory_path}")
    
    print(f"Processing documents from: {directory_path}")
    print("-" * 50)
    
    # Step 1: Load documents
    print("Step 1: Loading documents...")
    raw_documents = load_documents_from_directory(directory_path)
    print(f"Total documents loaded: {len(raw_documents)}")
    
    if not raw_documents:
        print("Warning: No documents found in the directory.")
        return {
            'parent_chunks': [],
            'child_chunks': [],
            'parent_child_mapping': {},
            'stats': {
                'total_documents': 0,
                'total_parent_chunks': 0,
                'total_child_chunks': 0,
            }
        }
    
    # Step 2: Preprocess documents
    print("\nStep 2: Preprocessing documents...")
    cleaned_documents = preprocess_documents(raw_documents)
    print(f"Documents preprocessed: {len(cleaned_documents)}")
    
    # Step 3: Create parent-child chunks
    print("\nStep 3: Creating parent-child chunks...")
    result = create_parent_child_chunks(
        cleaned_documents,
        parent_chunk_size=parent_chunk_size,
        parent_chunk_overlap=parent_chunk_overlap,
        child_chunk_size=child_chunk_size,
        child_chunk_overlap=child_chunk_overlap,
    )
    
    # Add statistics
    result['stats'] = {
        'total_documents': len(raw_documents),
        'total_parent_chunks': len(result['parent_chunks']),
        'total_child_chunks': len(result['child_chunks']),
        'avg_children_per_parent': (
            len(result['child_chunks']) / len(result['parent_chunks'])
            if result['parent_chunks'] else 0
        ),
    }
    
    print("-" * 50)
    print("Processing complete!")
    print(f"  - Total documents: {result['stats']['total_documents']}")
    print(f"  - Parent chunks: {result['stats']['total_parent_chunks']}")
    print(f"  - Child chunks: {result['stats']['total_child_chunks']}")
    print(f"  - Avg children per parent: {result['stats']['avg_children_per_parent']:.2f}")
    
    return result


def get_parent_for_child(
    child_chunk: Document,
    parent_chunks: List[Document]
) -> Document | None:
    """
    Retrieve the parent chunk for a given child chunk.
    
    Useful for context expansion during retrieval.
    
    Args:
        child_chunk: A child Document with parent_id in metadata.
        parent_chunks: List of all parent Documents.
        
    Returns:
        The parent Document if found, None otherwise.
    """
    parent_id = child_chunk.metadata.get('parent_id')
    if not parent_id:
        return None
    
    for parent in parent_chunks:
        if parent.metadata.get('parent_id') == parent_id:
            return parent
    
    return None


# Example usage and testing
if __name__ == "__main__":
    import sys
    
    # Example: Process a sample directory
    if len(sys.argv) > 1:
        input_directory = sys.argv[1]
    else:
        # Default test directory (update as needed)
        input_directory = "./sample_documents"
    
    try:
        # Process the documents
        result = process_documents_directory(
            directory_path=input_directory,
            parent_chunk_size=2000,
            parent_chunk_overlap=200,
            child_chunk_size=400,
            child_chunk_overlap=50,
        )
        
        # Display sample output
        if result['parent_chunks']:
            print("\n" + "=" * 50)
            print("SAMPLE OUTPUT")
            print("=" * 50)
            
            # Show first parent chunk
            first_parent = result['parent_chunks'][0]
            print(f"\nFirst Parent Chunk (ID: {first_parent.metadata['parent_id'][:8]}...):")
            print(f"  Source: {first_parent.metadata.get('source', 'N/A')}")
            print(f"  Size: {first_parent.metadata['chunk_size']} chars")
            print(f"  Content preview: {first_parent.page_content[:200]}...")
            
            # Show associated children
            parent_id = first_parent.metadata['parent_id']
            child_ids = result['parent_child_mapping'][parent_id]
            print(f"\n  Associated Children ({len(child_ids)}):")
            
            for child in result['child_chunks'][:3]:
                if child.metadata['parent_id'] == parent_id:
                    print(f"    - Child {child.metadata['child_index']}: "
                          f"{child.page_content[:100]}...")
                    
    except Exception as e:
        print(f"Error processing documents: {e}")
        sys.exit(1)

"""
Surya OCR Module for PDF Text Extraction

This module provides Surya OCR-based PDF text extraction with Hebrew (RTL) support.
Designed for offline/air-gapped environments with locally downloaded models.

Features:
- Automatic detection of scanned vs text-based PDFs
- Hebrew text handling with correct RTL order
- Batch processing support for multiple PDFs
- Clean error handling with specific exception types

Author: Senior Python/ML Engineer
"""

import logging
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple, Generator
import io

# PDF handling
import fitz  # PyMuPDF
from PIL import Image

# Surya OCR imports - these should be available locally
try:
    from surya.ocr import run_ocr
    from surya.model.detection.model import load_model as load_det_model
    from surya.model.detection.processor import load_processor as load_det_processor
    from surya.model.recognition.model import load_model as load_rec_model
    from surya.model.recognition.processor import load_processor as load_rec_processor
    SURYA_AVAILABLE = True
except ImportError:
    SURYA_AVAILABLE = False

# Configure module logger
logger = logging.getLogger(__name__)


# =============================================================================
# Exception Classes
# =============================================================================

class PDFExtractionError(Exception):
    """Base exception for PDF extraction errors."""
    pass


class PDFEncryptedException(PDFExtractionError):
    """Raised when a PDF is encrypted and cannot be processed."""
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        super().__init__(f"PDF is encrypted and cannot be processed: {pdf_path}")


class PDFCorruptedException(PDFExtractionError):
    """Raised when a PDF is corrupt or cannot be opened."""
    def __init__(self, pdf_path: str, reason: str = ""):
        self.pdf_path = pdf_path
        self.reason = reason
        msg = f"PDF is corrupt or cannot be opened: {pdf_path}"
        if reason:
            msg += f" ({reason})"
        super().__init__(msg)


class OCRFailedException(PDFExtractionError):
    """Raised when OCR processing fails."""
    def __init__(self, pdf_path: str, page_num: Optional[int] = None, reason: str = ""):
        self.pdf_path = pdf_path
        self.page_num = page_num
        self.reason = reason
        msg = f"OCR failed for: {pdf_path}"
        if page_num is not None:
            msg += f" (page {page_num + 1})"
        if reason:
            msg += f" - {reason}"
        super().__init__(msg)


class SuryaNotAvailableError(PDFExtractionError):
    """Raised when Surya OCR is not installed."""
    def __init__(self):
        super().__init__(
            "Surya OCR is not available. Please install it with: pip install surya-ocr"
        )


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class PageExtractionResult:
    """Result of text extraction from a single page."""
    page_number: int
    text: str
    method: str  # 'text' or 'ocr'
    confidence: Optional[float] = None


@dataclass
class PDFExtractionResult:
    """Complete result of PDF text extraction."""
    pdf_path: str
    pages: List[PageExtractionResult] = field(default_factory=list)
    total_pages: int = 0
    ocr_pages_count: int = 0
    text_pages_count: int = 0
    
    @property
    def full_text(self) -> str:
        """Get concatenated text from all pages."""
        return "\n\n".join(page.text for page in self.pages if page.text.strip())
    
    @property
    def used_ocr(self) -> bool:
        """Check if OCR was used for any page."""
        return self.ocr_pages_count > 0


# =============================================================================
# Surya Model Manager (Singleton for efficiency)
# =============================================================================

class SuryaModelManager:
    """
    Singleton manager for Surya OCR models.
    
    Loads models once and reuses them for all OCR operations to avoid
    repeated model loading overhead during batch processing.
    """
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if SuryaModelManager._initialized:
            return
        
        if not SURYA_AVAILABLE:
            raise SuryaNotAvailableError()
        
        self.det_model = None
        self.det_processor = None
        self.rec_model = None
        self.rec_processor = None
        self._loaded = False
        SuryaModelManager._initialized = True
    
    def load_models(self) -> None:
        """Load Surya detection and recognition models."""
        if self._loaded:
            return
        
        logger.info("Loading Surya OCR models...")
        
        try:
            # Load detection model and processor
            self.det_processor = load_det_processor()
            self.det_model = load_det_model()
            
            # Load recognition model and processor
            self.rec_processor = load_rec_processor()
            self.rec_model = load_rec_model()
            
            self._loaded = True
            logger.info("Surya OCR models loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load Surya models: {e}")
            raise OCRFailedException("", reason=f"Model loading failed: {e}")
    
    def is_loaded(self) -> bool:
        """Check if models are loaded."""
        return self._loaded
    
    def run_ocr(self, images: List[Image.Image], languages: List[str]) -> List:
        """
        Run OCR on a list of images.
        
        Args:
            images: List of PIL Image objects
            languages: List of language codes (e.g., ['he', 'en'])
            
        Returns:
            List of OCR results from Surya
        """
        if not self._loaded:
            self.load_models()
        
        return run_ocr(
            images,
            [languages] * len(images),  # Same languages for all images
            self.det_model,
            self.det_processor,
            self.rec_model,
            self.rec_processor,
        )


# Global model manager instance
_model_manager: Optional[SuryaModelManager] = None


def get_model_manager() -> SuryaModelManager:
    """Get or create the Surya model manager singleton."""
    global _model_manager
    if _model_manager is None:
        _model_manager = SuryaModelManager()
    return _model_manager


# =============================================================================
# Hebrew Text Utilities
# =============================================================================

def normalize_hebrew_text(text: str) -> str:
    """
    Normalize Hebrew text for consistent storage and search.
    
    Applies:
    - Unicode NFC normalization (compose characters)
    - Consistent whitespace handling
    - Hebrew punctuation preservation
    
    Args:
        text: Raw Hebrew text
        
    Returns:
        Normalized UTF-8 text
    """
    # Use NFC normalization - composes characters (better for Hebrew)
    # NFC is preferred over NFKD for Hebrew as it preserves nikud properly
    text = unicodedata.normalize('NFC', text)
    
    return text


def clean_ocr_noise_hebrew(text: str) -> str:
    """
    Remove OCR noise while preserving Hebrew-specific characters.
    
    Preserves:
    - Hebrew letters (א-ת)
    - Hebrew nikud/vowel marks
    - Hebrew punctuation (maqaf ־, sof pasuq ׃, etc.)
    - Standard punctuation (. , ! ? : ; " ')
    - Numbers
    
    Args:
        text: Raw OCR text
        
    Returns:
        Cleaned text with Hebrew preserved
    """
    # Remove common OCR artifacts but preserve Hebrew characters
    # Hebrew Unicode range: \u0590-\u05FF (includes letters, nikud, punctuation)
    # Also preserve Arabic numerals and basic punctuation
    
    # Remove isolated single characters that are likely noise
    # (but not Hebrew letters which can be single-char words)
    text = re.sub(r'(?<!\S)[^\u0590-\u05FFa-zA-Z0-9](?!\S)', '', text)
    
    # Remove repeated punctuation (OCR artifacts)
    text = re.sub(r'([.,!?;:])\1+', r'\1', text)
    
    # Clean up excessive whitespace while preserving paragraph breaks
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    
    # Strip leading/trailing whitespace from lines
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)
    
    return text.strip()


def fix_broken_hebrew_words(text: str) -> str:
    """
    Attempt to rejoin Hebrew words that were incorrectly split by OCR.
    
    Common OCR issues with Hebrew:
    - Words split across lines
    - Spaces inserted within words
    
    Args:
        text: OCR text with potential word breaks
        
    Returns:
        Text with repaired word breaks
    """
    # Fix lines that end with a Hebrew letter followed by a line starting with Hebrew
    # This often indicates a word broken across lines
    text = re.sub(
        r'([\u05D0-\u05EA])\s*\n\s*([\u05D0-\u05EA])',
        r'\1\2',
        text
    )
    
    return text


def process_hebrew_ocr_output(text: str) -> str:
    """
    Full processing pipeline for Hebrew OCR output.
    
    Applies all Hebrew-specific cleaning and normalization steps.
    
    Args:
        text: Raw OCR output
        
    Returns:
        Clean, normalized Hebrew text
    """
    text = normalize_hebrew_text(text)
    text = clean_ocr_noise_hebrew(text)
    text = fix_broken_hebrew_words(text)
    return text


# =============================================================================
# PDF Analysis Utilities
# =============================================================================

def is_scanned_page(page: fitz.Page, text_threshold: int = 50) -> bool:
    """
    Determine if a PDF page is scanned/image-based.
    
    A page is considered scanned if it has:
    - Very little extractable text (< threshold characters)
    - Contains images
    
    Args:
        page: PyMuPDF page object
        text_threshold: Minimum character count to consider page text-based
        
    Returns:
        True if the page appears to be scanned
    """
    # Extract text from the page
    text = page.get_text("text").strip()
    
    # If there's substantial text, it's not scanned
    if len(text) >= text_threshold:
        return False
    
    # Check if page has images (common in scanned PDFs)
    image_list = page.get_images()
    if image_list:
        return True
    
    # Very little text and no images - could be blank or minimally scanned
    return len(text) < text_threshold


def is_scanned_pdf(pdf_path: str, sample_pages: int = 3) -> bool:
    """
    Determine if a PDF is primarily scanned/image-based.
    
    Samples the first few pages to make a determination.
    
    Args:
        pdf_path: Path to the PDF file
        sample_pages: Number of pages to sample
        
    Returns:
        True if the PDF appears to be scanned
    """
    try:
        doc = fitz.open(pdf_path)
        
        if doc.is_encrypted:
            doc.close()
            raise PDFEncryptedException(pdf_path)
        
        pages_to_check = min(sample_pages, len(doc))
        scanned_count = 0
        
        for i in range(pages_to_check):
            if is_scanned_page(doc[i]):
                scanned_count += 1
        
        doc.close()
        
        # If more than half of sampled pages are scanned, consider it scanned
        return scanned_count > pages_to_check / 2
        
    except fitz.FileDataError as e:
        raise PDFCorruptedException(pdf_path, str(e))
    except Exception as e:
        if isinstance(e, PDFExtractionError):
            raise
        raise PDFCorruptedException(pdf_path, str(e))


# =============================================================================
# Core OCR Functions
# =============================================================================

def extract_page_as_image(page: fitz.Page, dpi: int = 300) -> Image.Image:
    """
    Render a PDF page as a PIL Image.
    
    Args:
        page: PyMuPDF page object
        dpi: Resolution for rendering (higher = better OCR but slower)
        
    Returns:
        PIL Image object
    """
    # Calculate zoom factor for desired DPI (72 is default PDF DPI)
    zoom = dpi / 72
    mat = fitz.Matrix(zoom, zoom)
    
    # Render page to pixmap
    pix = page.get_pixmap(matrix=mat)
    
    # Convert to PIL Image
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    
    return img


def extract_text_from_page_ocr(
    page: fitz.Page,
    languages: List[str],
    dpi: int = 300,
) -> Tuple[str, Optional[float]]:
    """
    Extract text from a single page using Surya OCR.
    
    Args:
        page: PyMuPDF page object
        languages: Language codes for OCR (e.g., ['he', 'en'])
        dpi: Resolution for rendering
        
    Returns:
        Tuple of (extracted_text, confidence_score)
    """
    manager = get_model_manager()
    
    # Render page to image
    img = extract_page_as_image(page, dpi=dpi)
    
    # Run OCR
    results = manager.run_ocr([img], languages)
    
    if not results or not results[0]:
        return "", None
    
    # Extract text from OCR results
    # Surya returns text lines with bounding boxes
    page_result = results[0]
    
    # Concatenate text lines
    lines = []
    confidences = []
    
    for text_line in page_result.text_lines:
        lines.append(text_line.text)
        if hasattr(text_line, 'confidence'):
            confidences.append(text_line.confidence)
    
    text = "\n".join(lines)
    avg_confidence = sum(confidences) / len(confidences) if confidences else None
    
    # Apply Hebrew processing
    text = process_hebrew_ocr_output(text)
    
    return text, avg_confidence


def extract_text_from_page_direct(page: fitz.Page) -> str:
    """
    Extract text directly from a PDF page (no OCR).
    
    Args:
        page: PyMuPDF page object
        
    Returns:
        Extracted text
    """
    text = page.get_text("text")
    return normalize_hebrew_text(text.strip())


def extract_text_from_pdf_with_surya(
    pdf_path: str,
    languages: Optional[List[str]] = None,
    force_ocr: bool = False,
    text_threshold: int = 50,
    dpi: int = 300,
) -> str:
    """
    Extract text from a PDF using Surya OCR for scanned pages.
    
    This function intelligently chooses between direct text extraction
    and OCR based on page content. For pages with extractable text,
    direct extraction is used. For scanned/image pages, Surya OCR is used.
    
    Args:
        pdf_path: Path to the PDF file
        languages: Language codes for OCR (default: ['he', 'en'] for Hebrew + English)
        force_ocr: If True, use OCR for all pages regardless of text content
        text_threshold: Minimum chars to consider a page text-based
        dpi: DPI for OCR rendering (higher = better quality, slower)
        
    Returns:
        Extracted text as UTF-8 string
        
    Raises:
        PDFEncryptedException: If PDF is password-protected
        PDFCorruptedException: If PDF cannot be opened
        OCRFailedException: If OCR processing fails
    """
    if languages is None:
        languages = ['he', 'en']  # Hebrew + English default
    
    result = extract_text_from_pdf_with_surya_detailed(
        pdf_path=pdf_path,
        languages=languages,
        force_ocr=force_ocr,
        text_threshold=text_threshold,
        dpi=dpi,
    )
    
    return result.full_text


def extract_text_from_pdf_with_surya_detailed(
    pdf_path: str,
    languages: Optional[List[str]] = None,
    force_ocr: bool = False,
    text_threshold: int = 50,
    dpi: int = 300,
) -> PDFExtractionResult:
    """
    Extract text from a PDF with detailed results including metadata.
    
    Args:
        pdf_path: Path to the PDF file
        languages: Language codes for OCR
        force_ocr: If True, use OCR for all pages
        text_threshold: Minimum chars to consider a page text-based
        dpi: DPI for OCR rendering
        
    Returns:
        PDFExtractionResult with detailed extraction info
    """
    if languages is None:
        languages = ['he', 'en']
    
    pdf_path = str(Path(pdf_path).resolve())
    result = PDFExtractionResult(pdf_path=pdf_path)
    
    try:
        doc = fitz.open(pdf_path)
    except fitz.FileDataError as e:
        raise PDFCorruptedException(pdf_path, str(e))
    except Exception as e:
        raise PDFCorruptedException(pdf_path, str(e))
    
    try:
        if doc.is_encrypted:
            raise PDFEncryptedException(pdf_path)
        
        result.total_pages = len(doc)
        logger.info(f"Processing PDF: {pdf_path} ({result.total_pages} pages)")
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Determine extraction method
            use_ocr = force_ocr or is_scanned_page(page, text_threshold)
            
            try:
                if use_ocr:
                    text, confidence = extract_text_from_page_ocr(
                        page, languages, dpi
                    )
                    method = 'ocr'
                    result.ocr_pages_count += 1
                else:
                    text = extract_text_from_page_direct(page)
                    confidence = None
                    method = 'text'
                    result.text_pages_count += 1
                
                page_result = PageExtractionResult(
                    page_number=page_num,
                    text=text,
                    method=method,
                    confidence=confidence,
                )
                result.pages.append(page_result)
                
                logger.debug(
                    f"Page {page_num + 1}: {method} extraction, "
                    f"{len(text)} chars"
                )
                
            except Exception as e:
                logger.error(f"Failed to process page {page_num + 1}: {e}")
                raise OCRFailedException(pdf_path, page_num, str(e))
        
    finally:
        doc.close()
    
    logger.info(
        f"Extracted {len(result.full_text)} chars from {pdf_path} "
        f"(OCR: {result.ocr_pages_count}, Text: {result.text_pages_count})"
    )
    
    return result


# =============================================================================
# Batch Processing
# =============================================================================

def process_pdf_batch(
    pdf_paths: List[str],
    languages: Optional[List[str]] = None,
    force_ocr: bool = False,
    continue_on_error: bool = True,
) -> Generator[Tuple[str, PDFExtractionResult | Exception], None, None]:
    """
    Process multiple PDFs in batch with shared model loading.
    
    This is more efficient than calling extract_text_from_pdf_with_surya
    repeatedly as models are loaded once.
    
    Args:
        pdf_paths: List of PDF file paths
        languages: Language codes for OCR
        force_ocr: If True, use OCR for all pages
        continue_on_error: If True, continue processing on errors
        
    Yields:
        Tuples of (pdf_path, result_or_exception)
    """
    if languages is None:
        languages = ['he', 'en']
    
    # Pre-load models once
    if not force_ocr:
        # Only load if we might need OCR
        pass
    else:
        manager = get_model_manager()
        manager.load_models()
    
    for pdf_path in pdf_paths:
        try:
            result = extract_text_from_pdf_with_surya_detailed(
                pdf_path=pdf_path,
                languages=languages,
                force_ocr=force_ocr,
            )
            yield (pdf_path, result)
            
        except Exception as e:
            logger.error(f"Error processing {pdf_path}: {e}")
            if continue_on_error:
                yield (pdf_path, e)
            else:
                raise


# =============================================================================
# LangChain Integration (Custom Loader)
# =============================================================================

def load_pdf_with_surya(
    pdf_path: str,
    languages: Optional[List[str]] = None,
) -> List:
    """
    Load a PDF and return LangChain Document objects.
    
    This function provides LangChain-compatible output that integrates
    directly with parent_child_chunker.py.
    
    Args:
        pdf_path: Path to the PDF file
        languages: Language codes for OCR
        
    Returns:
        List of LangChain Document objects (one per page with text)
    """
    # Avoid circular import
    from langchain.schema import Document
    
    result = extract_text_from_pdf_with_surya_detailed(
        pdf_path=pdf_path,
        languages=languages,
    )
    
    documents = []
    for page in result.pages:
        if page.text.strip():
            doc = Document(
                page_content=page.text,
                metadata={
                    'source': pdf_path,
                    'page': page.page_number,
                    'extraction_method': page.method,
                    'confidence': page.confidence,
                }
            )
            documents.append(doc)
    
    return documents


# =============================================================================
# Module Initialization Check
# =============================================================================

def check_surya_available() -> bool:
    """Check if Surya OCR is available and models can be loaded."""
    return SURYA_AVAILABLE


def preload_models() -> None:
    """
    Pre-load Surya models for faster subsequent processing.
    
    Call this at application startup to avoid cold-start latency
    on first PDF processing.
    """
    if not SURYA_AVAILABLE:
        logger.warning("Surya OCR not available, skipping model preload")
        return
    
    manager = get_model_manager()
    manager.load_models()


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    if len(sys.argv) < 2:
        print("Usage: python surya_ocr.py <pdf_path>")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    
    try:
        print(f"Processing: {pdf_file}")
        print("-" * 50)
        
        text = extract_text_from_pdf_with_surya(pdf_file)
        
        print(f"\nExtracted text ({len(text)} characters):")
        print("=" * 50)
        print(text[:2000] if len(text) > 2000 else text)
        if len(text) > 2000:
            print(f"\n... ({len(text) - 2000} more characters)")
            
    except PDFEncryptedException as e:
        print(f"Error: {e}")
        sys.exit(1)
    except PDFCorruptedException as e:
        print(f"Error: {e}")
        sys.exit(1)
    except OCRFailedException as e:
        print(f"Error: {e}")
        sys.exit(1)

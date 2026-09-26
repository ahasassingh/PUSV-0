"""
Document text extractors for TXT, PDF, and DOCX.
Extracts structured document units (paragraphs/pages/tables) with location metadata.
Deterministic extraction — No OCR (explicit warning on image-only/scanned PDFs).
"""

from typing import List, Dict, Any, Tuple
import io
import docx
from pypdf import PdfReader

class ExtractionError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)

class DocumentUnit:
    def __init__(self, text: str, page: int | None = None, section: str | None = None, location: str = ""):
        self.text = text.strip()
        self.page = page
        self.section = section
        self.location = location

def extract_txt(file_bytes: bytes) -> List[DocumentUnit]:
    """
    Extract structured units from plain text.
    Preserves line structure and non-empty blocks.
    """
    try:
        text = file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        try:
            text = file_bytes.decode("latin-1")
        except Exception as e:
            raise ExtractionError("CORRUPTED_FILE", f"Unable to decode text document: {str(e)}")

    lines = text.splitlines()
    units: List[DocumentUnit] = []
    
    current_block: List[str] = []
    current_line_num = 1
    start_line = 1

    for idx, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped:
            if current_block:
                block_text = " ".join(current_block)
                units.append(DocumentUnit(
                    text=block_text,
                    page=None,
                    section=None,
                    location=f"line-{start_line}-to-{idx-1}" if start_line != idx-1 else f"line-{start_line}"
                ))
                current_block = []
        else:
            if not current_block:
                start_line = idx
            current_block.append(stripped)

    if current_block:
        units.append(DocumentUnit(
            text=" ".join(current_block),
            page=None,
            section=None,
            location=f"line-{start_line}-to-{len(lines)}" if start_line != len(lines) else f"line-{start_line}"
        ))

    return units

def extract_pdf(file_bytes: bytes) -> List[DocumentUnit]:
    """
    Extract selectable text from PDF.
    Preserves page numbers and paragraph locations.
    Raises ExtractionError("EXTRACTION_FAILED_SCANNED_PDF") if no selectable text found.
    """
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
    except Exception as e:
        raise ExtractionError("MALFORMED_PDF", f"Failed to parse PDF document structure: {str(e)}")

    if len(reader.pages) == 0:
        raise ExtractionError("EMPTY_DOCUMENT", "PDF document contains 0 pages.")

    units: List[DocumentUnit] = []
    total_text_len = 0

    for page_idx, page in enumerate(reader.pages, start=1):
        try:
            page_text = page.extract_text() or ""
        except Exception:
            page_text = ""

        total_text_len += len(page_text.strip())
        
        # Split page into paragraphs
        paras = [p.strip() for p in page_text.split("\n\n") if p.strip()]
        if not paras:
            # Try single newlines if no double newlines
            paras = [p.strip() for p in page_text.splitlines() if p.strip()]

        for p_idx, para in enumerate(paras, start=1):
            units.append(DocumentUnit(
                text=para,
                page=page_idx,
                section=None,
                location=f"page-{page_idx}-paragraph-{p_idx}"
            ))

    if total_text_len == 0 or len(units) == 0:
        raise ExtractionError(
            "EXTRACTION_FAILED_SCANNED_PDF",
            "PDF contains no selectable text. OCR is not enabled in Phase 2."
        )

    return units

def extract_docx(file_bytes: bytes) -> List[DocumentUnit]:
    """
    Extract paragraphs and tables from DOCX document.
    Preserves headings/sections where available.
    """
    try:
        doc = docx.Document(io.BytesIO(file_bytes))
    except Exception as e:
        raise ExtractionError("MALFORMED_DOCX", f"Failed to parse DOCX document structure: {str(e)}")

    units: List[DocumentUnit] = []
    current_section = None
    para_count = 0

    # Extract paragraphs
    for idx, p in enumerate(doc.paragraphs, start=1):
        text = p.text.strip()
        if not text:
            continue
        
        para_count += 1
        # Detect Heading style
        if p.style and p.style.name and p.style.name.startswith("Heading"):
            current_section = text
        
        units.append(DocumentUnit(
            text=text,
            page=None,
            section=current_section,
            location=f"paragraph-{para_count}"
        ))

    # Extract tables
    for t_idx, table in enumerate(doc.tables, start=1):
        for r_idx, row in enumerate(table.rows, start=1):
            row_texts = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if row_texts:
                combined_row = " | ".join(row_texts)
                units.append(DocumentUnit(
                    text=combined_row,
                    page=None,
                    section=current_section,
                    location=f"table-{t_idx}-row-{r_idx}"
                ))

    return units

def extract_document_units(filename: str, file_bytes: bytes) -> List[DocumentUnit]:
    """
    Router for extracting DocumentUnits based on file extension.
    """
    lower = filename.lower()
    if lower.endswith(".txt"):
        return extract_txt(file_bytes)
    elif lower.endswith(".pdf"):
        return extract_pdf(file_bytes)
    elif lower.endswith(".docx"):
        return extract_docx(file_bytes)
    else:
        raise ExtractionError("UNSUPPORTED_TYPE", f"Unsupported file extension: {filename}")

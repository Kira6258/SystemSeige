import io
import logging

import pdfplumber
from fastapi import HTTPException, status

from app.core.config import settings

logger = logging.getLogger("clearfinance")

PDF_MAGIC_BYTES = b"%PDF-"
MIN_EXTRACTED_CHARS = 50


def validate_upload(filename: str, content: bytes) -> None:
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF files are accepted")

    max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"File exceeds {settings.MAX_UPLOAD_MB}MB limit")

    if len(content) == 0 or not content.startswith(PDF_MAGIC_BYTES):
        # Magic-byte check — catches a renamed .exe or any non-PDF payload, not just the extension.
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File is not a valid PDF")


def extract_text(content: bytes) -> str:
    try:
        text_parts = []
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return "\n".join(text_parts).strip()
    except Exception:
        logger.exception("[ERROR] pdf text extraction failed")
        return ""


def extract_text_with_ocr_fallback(content: bytes) -> str:
    text = extract_text(content)
    if len(text) >= MIN_EXTRACTED_CHARS:
        return text

    # Near-empty extraction likely means a scanned/image PDF — fall back to OCR.
    try:
        import pytesseract
        from pdf2image import convert_from_bytes

        images = convert_from_bytes(content)
        ocr_parts = [pytesseract.image_to_string(image) for image in images]
        ocr_text = "\n".join(ocr_parts).strip()
        return ocr_text if ocr_text else text
    except Exception:
        logger.exception("[ERROR] OCR fallback failed")
        return text


def extract_document_text(content: bytes) -> str:
    text = extract_text_with_ocr_fallback(content)
    if len(text) < MIN_EXTRACTED_CHARS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not extract readable text from this document",
        )
    return text

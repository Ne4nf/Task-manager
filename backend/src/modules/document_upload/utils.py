"""
Document utilities for file processing
"""
import os
from pathlib import Path
from typing import Tuple


def get_file_type(filename: str) -> str:
    """Determine file type from extension"""
    ext = Path(filename).suffix.lower()
    if ext == ".md":
        return "markdown"
    elif ext == ".docx":
        return "docx"
    elif ext == ".pdf":
        return "pdf"
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def read_markdown_file(content: bytes) -> str:
    """Read markdown file content"""
    return content.decode("utf-8")


def read_docx_file(content: bytes) -> str:
    """Read docx file content"""
    # TODO: Implement docx parsing with python-docx
    # For now, return placeholder
    return "[DOCX content - implementation pending]"


def read_pdf_file(content: bytes) -> str:
    """Read PDF file content"""
    # TODO: Implement PDF parsing with PyPDF2 or pdfplumber
    # For now, return placeholder
    return "[PDF content - implementation pending]"


def process_file_content(filename: str, content: bytes) -> Tuple[str, str]:
    """
    Process uploaded file and extract text content
    
    Returns:
        Tuple of (file_type, content_text)
    """
    file_type = get_file_type(filename)
    
    if file_type == "markdown":
        content_text = read_markdown_file(content)
    elif file_type == "docx":
        content_text = read_docx_file(content)
    elif file_type == "pdf":
        content_text = read_pdf_file(content)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")
    
    return file_type, content_text

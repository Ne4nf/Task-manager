"""
Document dependencies
"""
from fastapi import Depends
from supabase import Client
from src.core.database import get_supabase
from src.modules.document_upload.service import DocumentService


def get_document_service(db: Client = Depends(get_supabase)) -> DocumentService:
    return DocumentService(db)

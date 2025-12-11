"""
Document upload controller (API endpoints)
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from typing import List
from src.core.session import get_current_user_from_session
from src.modules.document_upload.schema import DocumentUploadResponse, DocumentListResponse
from src.modules.document_upload.service import DocumentService
from src.modules.document_upload.deps import get_document_service
from src.core.config import get_settings

router = APIRouter(prefix="/documents", tags=["documents"])
settings = get_settings()


@router.post("/upload/{project_id}", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    project_id: str,
    file: UploadFile = File(...),
    service: DocumentService = Depends(get_document_service),
    user_id: str = Depends(get_current_user_from_session)
):
    """
    Upload a project document (.md, .docx, or .pdf)
    
    Requires authentication - user_id automatically retrieved from session/header
    """
    # Validate file extension
    if not any(file.filename.endswith(ext) for ext in settings.ALLOWED_FILE_TYPES):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {', '.join(settings.ALLOWED_FILE_TYPES)}"
        )
    
    # Read file content
    content = await file.read()
    
    # Validate file size
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE / 1024 / 1024}MB"
        )
    
    try:
        document = await service.upload_document(project_id, file.filename, content, user_id)
        return document
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/project/{project_id}", response_model=List[DocumentListResponse])
async def get_project_documents(
    project_id: str,
    service: DocumentService = Depends(get_document_service)
):
    """Get all documents for a project"""
    documents = await service.get_documents_by_project(project_id)
    return documents


@router.get("/{document_id}", response_model=DocumentUploadResponse)
async def get_document(
    document_id: str,
    service: DocumentService = Depends(get_document_service)
):
    """Get document by ID with full content"""
    document = await service.get_document_by_id(document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found"
        )
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    service: DocumentService = Depends(get_document_service)
):
    """Delete document"""
    deleted = await service.delete_document(document_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found"
        )

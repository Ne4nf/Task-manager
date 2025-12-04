"""
Document upload schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class DocumentUploadResponse(BaseModel):
    id: str
    project_id: str
    filename: str
    file_type: str
    content: str
    file_size: int
    uploaded_by: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    id: str
    project_id: str
    filename: str
    file_type: str
    file_size: int
    uploaded_by: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

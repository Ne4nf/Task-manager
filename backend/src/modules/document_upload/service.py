"""
Document upload service
"""
from typing import List, Optional
from supabase import Client
from src.modules.document_upload.model import ProjectDocument
from src.modules.document_upload.utils import process_file_content


class DocumentService:
    def __init__(self, db: Client):
        self.db = db
    
    async def upload_document(
        self,
        project_id: str,
        filename: str,
        content: bytes,
        user_id: str
    ) -> dict:
        """Upload document for a project"""
        # Process file content
        file_type, content_text = process_file_content(filename, content)
        
        data = {
            "project_id": project_id,
            "filename": filename,
            "file_type": file_type,
            "content": content_text,
            "file_size": len(content),
            "uploaded_by": user_id,
        }
        
        response = self.db.table(ProjectDocument.table_name).insert(data).execute()
        return ProjectDocument.to_dict(response.data[0])
    
    async def get_documents_by_project(self, project_id: str) -> List[dict]:
        """Get all documents for a project"""
        response = self.db.table(ProjectDocument.table_name)\
            .select("*")\
            .eq("project_id", project_id)\
            .execute()
        
        return [ProjectDocument.to_dict(row) for row in response.data]
    
    async def get_document_by_id(self, document_id: str) -> Optional[dict]:
        """Get document by ID"""
        response = self.db.table(ProjectDocument.table_name)\
            .select("*")\
            .eq("id", document_id)\
            .execute()
        
        if response.data:
            return ProjectDocument.to_dict(response.data[0])
        return None
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete document"""
        response = self.db.table(ProjectDocument.table_name)\
            .delete()\
            .eq("id", document_id)\
            .execute()
        
        return len(response.data) > 0

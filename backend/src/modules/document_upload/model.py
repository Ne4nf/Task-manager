"""
Document model
"""


class ProjectDocument:
    table_name = "project_documents"
    
    @staticmethod
    def to_dict(row) -> dict:
        """Convert database row to dictionary"""
        return {
            "id": row.get("id"),
            "project_id": row.get("project_id"),
            "filename": row.get("filename"),
            "file_type": row.get("file_type"),
            "content": row.get("content"),
            "file_size": row.get("file_size"),
            "uploaded_by": row.get("uploaded_by"),
            "created_at": row.get("created_at"),
            "updated_at": row.get("updated_at"),
        }

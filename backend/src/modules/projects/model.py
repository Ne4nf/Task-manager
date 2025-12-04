"""
Project model
"""
from typing import Optional


class Project:
    table_name = "projects"
    
    @staticmethod
    def to_dict(row) -> dict:
        """Convert database row to dictionary"""
        return {
            "id": row.get("id"),
            "name": row.get("name"),
            "description": row.get("description"),
            "domain": row.get("domain"),
            "status": row.get("status", "active"),
            "module_count": row.get("module_count", 0),
            "task_count": row.get("task_count", 0),
            "completed_tasks": row.get("completed_tasks", 0),
            "progress": row.get("progress", 0),
            "created_by": row.get("created_by"),
            "created_at": row.get("created_at"),
            "updated_at": row.get("updated_at"),
        }

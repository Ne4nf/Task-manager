"""
Module model
"""


class Module:
    table_name = "modules"
    
    @staticmethod
    def to_dict(row) -> dict:
        """Convert database row to dictionary"""
        return {
            "id": row.get("id"),
            "project_id": row.get("project_id"),
            "name": row.get("name"),
            "description": row.get("description"),
            "scope": row.get("scope"),
            "dependencies": row.get("dependencies"),
            "features": row.get("features"),
            "requirements": row.get("requirements"),
            "technical_specs": row.get("technical_specs"),
            "progress": row.get("progress", 0),
            "task_count": row.get("task_count", 0),
            "completed_tasks": row.get("completed_tasks", 0),
            "generated_by_ai": row.get("generated_by_ai", False),
            "generation_metadata": row.get("generation_metadata", {}),
            "created_at": row.get("created_at"),
            "updated_at": row.get("updated_at"),
        }

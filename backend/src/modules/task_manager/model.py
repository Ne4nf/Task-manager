"""
Task model
"""


class Task:
    table_name = "tasks"
    
    @staticmethod
    def to_dict(row) -> dict:
        """Convert database row to dictionary"""
        return {
            "id": row.get("id"),
            "module_id": row.get("module_id"),
            "name": row.get("name"),
            "description": row.get("description"),
            "assignee": row.get("assignee"),
            "status": row.get("status", "todo"),
            "priority": row.get("priority", "medium"),
            "difficulty": row.get("difficulty", 2),
            "time_estimate": row.get("time_estimate", 0),
            "actual_time": row.get("actual_time", 0),
            "quality_score": row.get("quality_score", 3),
            "autonomy": row.get("autonomy", 2),
            "due_date": row.get("due_date"),
            "started_at": row.get("started_at"),
            "completed_at": row.get("completed_at"),
            "generated_by_ai": row.get("generated_by_ai", False),
            "generation_metadata": row.get("generation_metadata", {}),
            "created_at": row.get("created_at"),
            "updated_at": row.get("updated_at"),
        }

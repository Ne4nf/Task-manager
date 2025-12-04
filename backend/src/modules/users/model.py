"""
User model
"""
from typing import Any, Dict


class User:
    table_name = "users"
    
    @staticmethod
    def to_dict(row: Dict[str, Any]) -> Dict[str, Any]:
        """Convert database row to dictionary"""
        return {
            "id": row.get("id"),
            "email": row.get("email"),
            "full_name": row.get("full_name"),
            "created_at": row.get("created_at"),
        }

"""
User dependencies
"""
from src.modules.users.service import UserService
from src.core.database import SupabaseClient


def get_user_service() -> UserService:
    """Get user service instance"""
    db = SupabaseClient.get_client()
    return UserService(db)

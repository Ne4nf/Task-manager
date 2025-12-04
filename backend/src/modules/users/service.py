"""
User service
"""
from typing import Optional
from supabase import Client
from src.modules.users.schema import UserCreate
from src.modules.users.model import User


class UserService:
    def __init__(self, db: Client):
        self.db = db
    
    async def get_user_by_email(self, email: str) -> Optional[dict]:
        """Get user by email"""
        response = self.db.table(User.table_name)\
            .select("*")\
            .eq("email", email)\
            .execute()
        
        if response.data:
            return User.to_dict(response.data[0])
        return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[dict]:
        """Get user by ID"""
        response = self.db.table(User.table_name)\
            .select("*")\
            .eq("id", user_id)\
            .execute()
        
        if response.data:
            return User.to_dict(response.data[0])
        return None
    
    async def create_user(self, user: UserCreate) -> dict:
        """Create new user"""
        data = {
            "email": user.email,
            "full_name": user.full_name,
        }
        
        response = self.db.table(User.table_name).insert(data).execute()
        return User.to_dict(response.data[0])

"""
Supabase database client
"""
from supabase import create_client, Client
from src.core.config import get_settings

settings = get_settings()


class SupabaseClient:
    _instance: Client = None
    
    @classmethod
    def get_client(cls) -> Client:
        if cls._instance is None:
            cls._instance = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_SERVICE_KEY
            )
        return cls._instance


def get_supabase() -> Client:
    return SupabaseClient.get_client()

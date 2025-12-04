"""
Core dependencies
"""
from src.core.database import get_supabase
from src.core.claude import get_claude

__all__ = ["get_supabase", "get_claude"]

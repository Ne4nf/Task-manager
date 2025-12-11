"""
Git Analyzer Dependencies
Dependency injection for services
"""
from fastapi import Depends
from supabase import Client
from src.core.database import get_supabase
from .service import GitAnalyzerService


def get_git_analyzer_service(db: Client = Depends(get_supabase)) -> GitAnalyzerService:
    """
    Dependency to get GitAnalyzerService instance with database
    
    Args:
        db: Supabase client
    
    Returns:
        GitAnalyzerService instance
    """
    return GitAnalyzerService(db=db)

"""
Project dependencies
"""
from fastapi import Depends
from supabase import Client
from src.core.database import get_supabase
from src.modules.projects.service import ProjectService


def get_project_service(db: Client = Depends(get_supabase)) -> ProjectService:
    return ProjectService(db)

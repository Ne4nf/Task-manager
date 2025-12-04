"""
Task manager dependencies
"""
from fastapi import Depends
from supabase import Client
import anthropic
from src.core.database import get_supabase
from src.core.claude import get_claude
from src.modules.task_manager.service import TaskService


def get_task_service(
    db: Client = Depends(get_supabase),
    claude: anthropic.Anthropic = Depends(get_claude)
) -> TaskService:
    return TaskService(db, claude)

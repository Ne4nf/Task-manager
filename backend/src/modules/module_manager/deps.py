"""
Module manager dependencies
"""
from fastapi import Depends
from supabase import Client
import anthropic
from src.core.database import get_supabase
from src.core.claude import get_claude
from src.modules.module_manager.service import ModuleService


def get_module_service(
    db: Client = Depends(get_supabase),
    claude: anthropic.Anthropic = Depends(get_claude)
) -> ModuleService:
    return ModuleService(db, claude)

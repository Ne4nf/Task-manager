"""
Claude AI client for module and task generation
"""
import anthropic
from src.core.config import get_settings

settings = get_settings()


class ClaudeClient:
    _instance: anthropic.Anthropic = None
    
    @classmethod
    def get_client(cls) -> anthropic.Anthropic:
        if cls._instance is None:
            cls._instance = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        return cls._instance


def get_claude() -> anthropic.Anthropic:
    return ClaudeClient.get_client()

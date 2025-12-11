"""
Git Analyzer Schemas - Simplified for Phase 1
Request/Response models for Git repository analysis
"""
from typing import Optional
from pydantic import BaseModel, Field


# ==================== REQUEST SCHEMA ====================

class AnalyzeRepositoryRequest(BaseModel):
    """Request to analyze a Git repository"""
    git_url: str = Field(..., description="Git repository URL (https)")
    project_id: str = Field(..., description="Project ID to save analysis to")
    access_token: Optional[str] = Field(None, description="GitHub access token for private repos")
    
    class Config:
        json_schema_extra = {
            "example": {
                "git_url": "https://github.com/username/repo",
                "project_id": "uuid-of-project",
                "access_token": "ghp_xxxxxxxxxxxxx"
            }
        }


# ==================== RESPONSE SCHEMA ====================

class AnalyzeRepositoryResponse(BaseModel):
    """Response from repository analysis"""
    git_url: str
    repo_name: str
    owner: str
    analysis_markdown: str = Field(..., description="Full markdown analysis from Claude")
    status: str = Field(..., description="completed or failed")
    error: Optional[str] = Field(None, description="Error message if failed")
    document_id: Optional[str] = Field(None, description="ID of saved document in project_documents")
    
    class Config:
        json_schema_extra = {
            "example": {
                "git_url": "https://github.com/fastapi/fastapi",
                "repo_name": "fastapi",
                "owner": "fastapi",
                "analysis_markdown": "# FastAPI - (Claude review SKILL.md)\n\n**Executive Summary**...",
                "status": "completed",
                "error": None
            }
        }

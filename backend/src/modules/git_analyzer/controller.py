"""
Git Analyzer Controller - Simplified for Phase 1
Single API endpoint: POST /analyze - Analyze Git repository and return markdown summary
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict

from .schema import AnalyzeRepositoryRequest, AnalyzeRepositoryResponse
from .service import GitAnalyzerService
from .deps import get_git_analyzer_service

router = APIRouter(prefix="/git-analyzer", tags=["Git Analyzer"])


@router.post("/analyze", response_model=AnalyzeRepositoryResponse)
async def analyze_repository(
    request: AnalyzeRepositoryRequest,
    service: GitAnalyzerService = Depends(get_git_analyzer_service)
) -> Dict:
    """
    Analyze a Git repository and return comprehensive markdown summary
    
    Phase 1: Simple workflow - Git URL → Repomix → Claude AI → Markdown
    
    Args:
        request: Git URL and optional access token for private repos
        
    Returns:
        AnalyzeRepositoryResponse with full markdown analysis
        
    Example:
        POST /api/v1/git-analyzer/analyze
        {
            "git_url": "https://github.com/fastapi/fastapi",
            "access_token": "ghp_xxxxx"  // optional for private repos
        }
        
        Response:
        {
            "git_url": "https://github.com/fastapi/fastapi",
            "repo_name": "fastapi",
            "owner": "fastapi",
            "analysis_markdown": "# FastAPI - (Claude review SKILL.md)\n\n**Executive Summary**...",
            "status": "completed",
            "error": null
        }
    """
    try:
        result = await service.analyze_repository(
            git_url=request.git_url,
            project_id=request.project_id,
            access_token=request.access_token
        )
        return result
        
    except ValueError as e:
        # Validation errors (invalid URL, unsupported host, etc.)
        raise HTTPException(status_code=400, detail=str(e))
        
    except RuntimeError as e:
        # Runtime errors (Repomix failed, Claude API failed, etc.)
        raise HTTPException(status_code=500, detail=str(e))
        
    except Exception as e:
        # Unexpected errors
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error during analysis: {str(e)}"
        )

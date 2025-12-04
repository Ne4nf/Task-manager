"""
Project controller (API endpoints)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from src.modules.projects.schema import ProjectCreate, ProjectUpdate, ProjectResponse
from src.modules.projects.service import ProjectService
from src.modules.projects.deps import get_project_service

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=List[ProjectResponse])
async def get_all_projects(
    service: ProjectService = Depends(get_project_service)
):
    """Get all projects"""
    projects = await service.get_all_projects()
    return projects


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    service: ProjectService = Depends(get_project_service)
):
    """Get project by ID"""
    project = await service.get_project_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found"
        )
    return project


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate,
    service: ProjectService = Depends(get_project_service)
):
    """Create new project"""
    # TODO: Get user_id from auth token
    user_id = "00000000-0000-0000-0000-000000000000"
    
    created_project = await service.create_project(project, user_id)
    return created_project


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    project: ProjectUpdate,
    service: ProjectService = Depends(get_project_service)
):
    """Update project"""
    updated_project = await service.update_project(project_id, project)
    if not updated_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found"
        )
    return updated_project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    service: ProjectService = Depends(get_project_service)
):
    """Delete project"""
    deleted = await service.delete_project(project_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found"
        )

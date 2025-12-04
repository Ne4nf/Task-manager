"""
Task manager controller (API endpoints)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from src.modules.task_manager.schema import (
    TaskCreate, TaskUpdate, TaskResponse,
    GenerateTasksRequest, GenerateTasksResponse
)
from src.modules.task_manager.service import TaskService
from src.modules.task_manager.deps import get_task_service
from src.modules.module_manager.service import ModuleService
from src.modules.module_manager.deps import get_module_service

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/module/{module_id}", response_model=List[TaskResponse])
async def get_module_tasks(
    module_id: str,
    service: TaskService = Depends(get_task_service)
):
    """Get all tasks for a module"""
    tasks = await service.get_tasks_by_module(module_id)
    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    service: TaskService = Depends(get_task_service)
):
    """Get task by ID"""
    task = await service.get_task_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    return task


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate,
    service: TaskService = Depends(get_task_service)
):
    """Create new task"""
    created_task = await service.create_task(task)
    return created_task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task: TaskUpdate,
    service: TaskService = Depends(get_task_service)
):
    """Update task"""
    updated_task = await service.update_task(task_id, task)
    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    return updated_task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    service: TaskService = Depends(get_task_service)
):
    """Delete task"""
    deleted = await service.delete_task(task_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )


@router.post("/generate", response_model=GenerateTasksResponse)
async def generate_tasks_with_ai(
    request: GenerateTasksRequest,
    task_service: TaskService = Depends(get_task_service),
    module_service: ModuleService = Depends(get_module_service)
):
    """
    Generate tasks using Claude AI based on module specifications
    """
    # Get module data
    module = await module_service.get_module_by_id(request.module_id)
    
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module {request.module_id} not found"
        )
    
    try:
        # Generate tasks with AI
        tasks = await task_service.generate_tasks_with_ai(
            module_id=request.module_id,
            module_data=module
        )
        
        return GenerateTasksResponse(
            tasks=tasks,
            message=f"Successfully generated {len(tasks)} tasks using AI"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate tasks: {str(e)}"
        )

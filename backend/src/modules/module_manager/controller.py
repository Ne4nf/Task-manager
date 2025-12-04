"""
Module manager controller (API endpoints)
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import List
from src.modules.module_manager.schema import (
    ModuleCreate, ModuleUpdate, ModuleResponse,
    GenerateModulesRequest, GenerateModulesResponse
)
from src.modules.module_manager.service import ModuleService
from src.modules.module_manager.deps import get_module_service
from src.modules.document_upload.service import DocumentService
from src.modules.document_upload.deps import get_document_service

router = APIRouter(prefix="/modules", tags=["modules"])


@router.get("/project/{project_id}", response_model=List[ModuleResponse])
async def get_project_modules(
    project_id: str,
    service: ModuleService = Depends(get_module_service)
):
    """Get all modules for a project"""
    modules = await service.get_modules_by_project(project_id)
    return modules


@router.get("/{module_id}", response_model=ModuleResponse)
async def get_module(
    module_id: str,
    service: ModuleService = Depends(get_module_service)
):
    """Get module by ID"""
    module = await service.get_module_by_id(module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module {module_id} not found"
        )
    return module


@router.post("", response_model=ModuleResponse, status_code=status.HTTP_201_CREATED)
async def create_module(
    module: ModuleCreate,
    service: ModuleService = Depends(get_module_service)
):
    """Create new module"""
    created_module = await service.create_module(module)
    return created_module


@router.put("/{module_id}", response_model=ModuleResponse)
async def update_module(
    module_id: str,
    module: ModuleUpdate,
    service: ModuleService = Depends(get_module_service)
):
    """Update module"""
    updated_module = await service.update_module(module_id, module)
    if not updated_module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module {module_id} not found"
        )
    return updated_module


@router.delete("/{module_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_module(
    module_id: str,
    service: ModuleService = Depends(get_module_service)
):
    """Delete module"""
    deleted = await service.delete_module(module_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module {module_id} not found"
        )


@router.post("/generate", response_model=GenerateModulesResponse)
async def generate_modules_with_ai(
    request: GenerateModulesRequest,
    module_service: ModuleService = Depends(get_module_service),
    document_service: DocumentService = Depends(get_document_service)
):
    """
    Generate modules using Claude AI based on uploaded project documentation
    """
    # Get project documents
    documents = await document_service.get_documents_by_project(request.project_id)
    
    if not documents:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No documentation found for this project. Please upload a project document first."
        )
    
    # Use specific document if provided, otherwise use the latest one
    if request.document_id:
        document = await document_service.get_document_by_id(request.document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {request.document_id} not found"
            )
    else:
        # Use the most recent document
        document = max(documents, key=lambda d: d['created_at'])
    
    documentation = document['content']
    
    try:
        # Generate modules with AI
        modules = await module_service.generate_modules_with_ai(
            project_id=request.project_id,
            documentation=documentation
        )
        
        return GenerateModulesResponse(
            modules=modules,
            message=f"Successfully generated {len(modules)} modules using AI"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate modules: {str(e)}"
        )

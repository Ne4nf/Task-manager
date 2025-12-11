"""
Module manager controller (API endpoints) with tag generation and search
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import List
from src.modules.module_manager.schema import (
    ModuleCreate, ModuleUpdate, ModuleResponse,
    GenerateModulesRequest, GenerateModulesResponse,
    GenerateTagsRequest, GenerateTagsResponse,
    SearchModulesRequest, SearchModulesResponse,
    ScoringWeightsConfigResponse
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


@router.post("/generate-direct", response_model=GenerateModulesResponse)
async def generate_modules_direct(
    request: GenerateModulesRequest,
    module_service: ModuleService = Depends(get_module_service),
    document_service: DocumentService = Depends(get_document_service)
):
    """
    🔧 DIRECT GENERATION: Generate modules from documentation WITHOUT searching memories.
    
    Use this for:
    - Git-analyzed repositories (complete codebase)
    - Self-contained documents
    - When you want fresh analysis without reuse
    
    This endpoint:
    1. Reads project documentation
    2. Generates modules directly using AI
    3. Saves with source_type='git_analyzed' or 'ai_generated'
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
    
    # Check if from git analyzer (metadata flag)
    doc_metadata = document.get('metadata', {})
    is_git_analysis = doc_metadata.get('from_git_analyzer', False)
    
    try:
        print(f"🔧 Direct generation mode (from_git: {is_git_analysis})")
        
        # Direct generation - no memory search
        source_type = "git_analyzed" if is_git_analysis else "ai_generated"
        modules = await module_service.generate_modules_with_ai(
            project_id=request.project_id,
            documentation=documentation,
            source_type=source_type
        )
        
        message = f"Generated {len(modules)} modules using direct analysis"
        
        return GenerateModulesResponse(
            modules=modules,
            message=message
        )
        
    except Exception as e:
        import traceback
        print(f"Error generating modules: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate modules: {str(e)}"
        )


@router.post("/generate-with-memories", response_model=GenerateModulesResponse)
async def generate_modules_with_memories(
    request: GenerateModulesRequest,
    module_service: ModuleService = Depends(get_module_service),
    document_service: DocumentService = Depends(get_document_service)
):
    """
    📝 MEMORY-BASED GENERATION: Generate modules WITH memory search and reuse.
    
    Use this for:
    - Manual requirements documents
    - New project ideas
    - When you want to leverage past projects
    
    This endpoint:
    1. Extracts tags from requirements (L1-L4)
    2. Searches for similar modules in database
    3. Analyzes top matches:
       - Score ≥ 0.85: Direct reuse (copy + customize)
       - 0.60-0.85: Pattern combination (synthesize from multiple references)
       - < 0.60: Generate new from scratch
    4. Returns modules + reuse summary + suggestions
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
        print("📝 Memory-based generation mode")
        
        # Get config name from request or use default
        config_name = getattr(request, 'config_name', 'default')
        top_k = getattr(request, 'top_k', 3)
        
        # Memory-based generation with search
        result = await module_service.generate_modules_with_memory_search(
            project_id=request.project_id,
            requirements_doc=documentation,
            config_name=config_name,
            top_k=top_k
        )
        
        modules = result['modules']
        message = result['message']
        
        # Return with reuse information
        return GenerateModulesResponse(
            modules=modules,
            message=message,
            reuse_summary=result.get('reuse_summary'),
            reuse_suggestions=result.get('top_matches')
        )
        
    except Exception as e:
        import traceback
        print(f"Error in memory-based generation: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate modules with memories: {str(e)}"
        )


@router.post("/generate-with-per-module-search", response_model=GenerateModulesResponse)
async def generate_modules_with_per_module_search(
    request: GenerateModulesRequest,
    module_service: ModuleService = Depends(get_module_service),
    document_service: DocumentService = Depends(get_document_service)
):
    """
    🆕 PER-MODULE SEARCH GENERATION: Most accurate approach (Issue #3 solution).
    
    NEW WORKFLOW:
    1. Break requirements into module outlines (4-8 modules)
    2. For EACH module:
       - Extract tags specific to that module's description
       - Search memories for similar modules using module-specific tags
       - Reuse/adapt based on similarity for that module
    3. Auto-tag all created modules
    
    WHY THIS IS BETTER THAN generate-with-memories:
    - More precise matching: Auth module finds Auth memories, not Inventory
    - Per-module L1 intent matching (not global tags for all modules)
    - Better reuse rate due to targeted search
    
    Use this for:
    - Complex requirements with multiple modules
    - When accuracy is critical
    - Production-ready module generation
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
        print("🔍 Per-module search generation mode (Issue #3 solution)")
        
        # Get config name from request or use default
        config_name = getattr(request, 'config_name', 'default')
        top_k_per_module = getattr(request, 'top_k', 3)
        
        # Per-module search generation
        result = await module_service.generate_modules_with_per_module_search(
            project_id=request.project_id,
            requirements_doc=documentation,
            config_name=config_name,
            top_k_per_module=top_k_per_module
        )
        
        modules = result['modules']
        message = result['message']
        
        # Return with per-module search details
        return GenerateModulesResponse(
            modules=modules,
            message=message,
            reuse_summary=result.get('reuse_summary'),
            reuse_suggestions=result.get('module_search_details')  # Per-module details
        )
        
    except Exception as e:
        import traceback
        print(f"Error in per-module generation: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate modules with per-module search: {str(e)}"
        )


@router.post("/{module_id}/regenerate-details", response_model=ModuleResponse)
async def regenerate_module_details(
    module_id: str,
    module_service: ModuleService = Depends(get_module_service),
    document_service: DocumentService = Depends(get_document_service)
):
    """
    Regenerate Phase 2 details (features, requirements, technical_specs) for a module
    that failed or has incomplete details.
    """
    # Get the module
    module = await module_service.get_module_by_id(module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module {module_id} not found"
        )
    
    # Get project documentation
    documents = await document_service.get_documents_by_project(module['project_id'])
    if not documents:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No documentation found for this project"
        )
    
    documentation = max(documents, key=lambda d: d['created_at'])['content']
    
    try:
        # Regenerate only Phase 2 details
        updated_module = await module_service.regenerate_module_details(
            module_id=module_id,
            module=module,
            documentation=documentation
        )
        
        return updated_module
    except Exception as e:
        import traceback
        print(f"Error regenerating module details: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to regenerate module details: {str(e)}"
        )


# ================================================================
# NEW: Tag Generation & Module Search Endpoints
# ================================================================

@router.post("/{module_id}/generate-tags", response_model=GenerateTagsResponse)
async def generate_module_tags(
    module_id: str,
    service: ModuleService = Depends(get_module_service)
):
    """
    Generate 4-layer tags for a module using AI.
    
    This endpoint analyzes the module's description, features, requirements,
    and technical specs to automatically assign tags across 4 layers:
    - L1 Intent: Functional purpose (Auth, Payment, etc.)
    - L2 Constraint: Technical stack (Node.js, React, etc.)
    - L3 Context: Business domain (Fintech, E-commerce, etc.)
    - L4 Quality: Non-functional attributes (High-Traffic, etc.)
    """
    try:
        result = await service.generate_tags_for_module(module_id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        import traceback
        print(f"Error generating tags: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate tags: {str(e)}"
        )


@router.post("/search", response_model=SearchModulesResponse)
async def search_modules(
    request: SearchModulesRequest,
    service: ModuleService = Depends(get_module_service)
):
    """
    Search for modules similar to target requirements.
    
    Uses Hybrid Weighted Scoring to find reusable modules:
    - Calculates Jaccard similarity for each layer
    - Applies configurable weights (default: L1=50%, L2=25%, L3=15%, L4=10%)
    - Returns ranked results with reuse recommendations:
      * Score ≥ 0.85: Direct reuse (copy & adapt)
      * 0.60-0.85: Logic reference (extract patterns)
      * < 0.60: Generate new (no match)
    """
    try:
        results = await service.search_similar_modules(
            target_tags=request.target_tags,
            project_id=request.project_id,
            config_name=request.config_name,
            limit=request.limit
        )
        return results
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        import traceback
        print(f"Error searching modules: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Module search failed: {str(e)}"
        )


@router.get("/scoring-configs", response_model=List[ScoringWeightsConfigResponse])
async def get_scoring_configs(
    active_only: bool = True,
    service: ModuleService = Depends(get_module_service)
):
    """
    Get available scoring weight configurations.
    
    Returns list of configs with different weight strategies:
    - 'default': Intent-first (50%, 25%, 15%, 10%)
    - 'tech_agnostic': Logic-focused (60%, 10%, 25%, 5%)
    
    Each config includes thresholds for decision zones.
    """
    try:
        configs = await service.get_scoring_configs(active_only=active_only)
        return configs
    except Exception as e:
        import traceback
        print(f"Error fetching configs: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch scoring configs: {str(e)}"
        )

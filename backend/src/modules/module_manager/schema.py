"""
Module manager schemas with 4-layer metadata support
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Literal
from datetime import datetime


class ModuleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    scope: Optional[str] = None
    dependencies: Optional[str] = None
    features: Optional[str] = None
    requirements: Optional[str] = None
    technical_specs: Optional[str] = None


class ModuleCreate(ModuleBase):
    project_id: str
    # Optional: Can provide tags upfront
    source_type: Optional[Literal['git_analyzed', 'manual_upload', 'ai_generated', 'reused']] = 'manual_upload'
    intent_primary: Optional[str] = None
    tags_metadata: Optional[Dict[str, Any]] = None


class ModuleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    scope: Optional[str] = None
    dependencies: Optional[str] = None
    features: Optional[str] = None
    requirements: Optional[str] = None
    technical_specs: Optional[str] = None
    intent_primary: Optional[str] = None
    tags_metadata: Optional[Dict[str, Any]] = None


class ModuleResponse(ModuleBase):
    id: str
    project_id: str
    progress: int
    task_count: int
    completed_tasks: int
    generated_by_ai: bool
    # New fields
    source_type: Optional[str] = None
    intent_primary: Optional[str] = None
    tags_metadata: Optional[Dict[str, Any]] = None
    reused_from_module_id: Optional[str] = None
    reuse_strategy: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class GenerateModulesRequest(BaseModel):
    project_id: str
    document_id: Optional[str] = None
    # Optional: For memory-based generation
    config_name: str = 'default'  # Which scoring config to use
    top_k: int = Field(default=3, ge=1, le=10)  # How many references to consider


class GenerateModulesResponse(BaseModel):
    modules: list[ModuleResponse]
    message: str
    # Optional: Reuse information (only for memory-based generation)
    reuse_summary: Optional[Dict[str, Any]] = None
    reuse_suggestions: Optional[List[Dict[str, Any]]] = None


# New schemas for tag management (3 layers only - MVP)
class ModuleTagCreate(BaseModel):
    module_id: str
    layer: Literal['L1_intent', 'L2_constraint', 'L3_context']
    tag_value: str
    confidence_score: float = Field(default=0.8, ge=0.0, le=1.0)
    tag_metadata: Optional[Dict[str, Any]] = None


class ModuleTagResponse(BaseModel):
    id: str
    module_id: str
    layer: str
    tag_value: str
    confidence_score: float
    tag_metadata: Optional[Dict[str, Any]] = None
    assigned_by: str
    assigned_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class ReuseHistoryResponse(BaseModel):
    id: str
    source_module_id: str
    target_module_id: str
    target_project_id: str
    similarity_score: float
    score_breakdown: Dict[str, Any]
    reuse_strategy: str
    decision_rationale: Optional[str] = None
    user_accepted: Optional[bool] = None
    user_feedback: Optional[str] = None
    ai_model: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ScoringWeightsConfigResponse(BaseModel):
    id: str
    config_name: str
    description: Optional[str] = None
    project_domain: Optional[str] = None
    target_tech_stack: Optional[str] = None
    weight_L1_intent: float
    weight_L2_constraint: float
    weight_L3_context: float
    weight_L4_quality: float
    threshold_direct_reuse: float
    threshold_logic_reference: float
    is_active: bool
    is_default: bool
    usage_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class GenerateTagsRequest(BaseModel):
    """Request to AI-generate tags for a module"""
    module_id: str


class GenerateTagsResponse(BaseModel):
    """Response with AI-generated tags"""
    module_id: str
    tags_generated: int
    tags_metadata: Dict[str, Any]
    message: str


class SearchModulesRequest(BaseModel):
    """Request to search for reusable modules"""
    target_tags: Dict[str, List[str]]  # {L1_intent: [...], L2_constraint: [...], ...}
    project_id: Optional[str] = None  # Exclude modules from this project
    config_name: str = 'default'
    limit: int = Field(default=10, ge=1, le=50)


class ModuleMatchResult(BaseModel):
    """Single module match result with score"""
    module: ModuleResponse
    similarity_score: float
    score_breakdown: Dict[str, Any]
    recommended_strategy: Literal['direct', 'logic_reference', 'new_gen']
    decision_rationale: str


class SearchModulesResponse(BaseModel):
    """Response with matched modules ranked by score"""
    matches: List[ModuleMatchResult]
    total_searched: int
    config_used: str

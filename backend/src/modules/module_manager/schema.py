"""
Module manager schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
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


class ModuleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    scope: Optional[str] = None
    dependencies: Optional[str] = None
    features: Optional[str] = None
    requirements: Optional[str] = None
    technical_specs: Optional[str] = None


class ModuleResponse(ModuleBase):
    id: str
    project_id: str
    progress: int
    task_count: int
    completed_tasks: int
    generated_by_ai: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class GenerateModulesRequest(BaseModel):
    project_id: str
    document_id: Optional[str] = None


class GenerateModulesResponse(BaseModel):
    modules: list[ModuleResponse]
    message: str

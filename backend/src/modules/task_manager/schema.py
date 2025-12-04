"""
Task manager schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date


class TaskBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    assignee: Optional[str] = None
    status: str = Field(default="todo", pattern="^(todo|in-progress|in-review|blocked|done)$")
    priority: str = Field(default="medium", pattern="^(low|medium|high)$")
    difficulty: int = Field(default=2, ge=1, le=5)
    time_estimate: float = Field(default=0, ge=0)
    quality_score: int = Field(default=3, ge=1, le=5)
    autonomy: int = Field(default=2, ge=1, le=4)
    due_date: Optional[date] = None


class TaskCreate(TaskBase):
    module_id: str


class TaskUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    assignee: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(todo|in-progress|in-review|blocked|done)$")
    priority: Optional[str] = Field(None, pattern="^(low|medium|high)$")
    difficulty: Optional[int] = Field(None, ge=1, le=5)
    time_estimate: Optional[float] = Field(None, ge=0)
    actual_time: Optional[float] = Field(None, ge=0)
    quality_score: Optional[int] = Field(None, ge=1, le=5)
    autonomy: Optional[int] = Field(None, ge=1, le=4)
    due_date: Optional[date] = None


class TaskResponse(TaskBase):
    id: str
    module_id: str
    actual_time: float
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    generated_by_ai: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class GenerateTasksRequest(BaseModel):
    module_id: str


class GenerateTasksResponse(BaseModel):
    tasks: list[TaskResponse]
    message: str

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum
import uuid

class TaskStatus(str, Enum):
    PARKING_LOT = "parking_lot"
    TODO = "todo"
    IN_PROGRESS = "inprogress"
    DONE = "done"

class ApprovalStatus(str, Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    AUTO_APPROVED = "auto_approved"

# Memory Management Models
class MemoryContextRequest(BaseModel):
    context: str = Field(..., description="Context text to store in memory")

class MemoryContextResponse(BaseModel):
    success: bool
    message: str
    memory_id: Optional[str] = None

class MemoryContextListResponse(BaseModel):
    contexts: List[Dict[str, Any]]
    total_count: int

# Task Models
class TaskBase(BaseModel):
    title: str = Field(..., max_length=500)
    status: TaskStatus = TaskStatus.TODO
    rank: int = Field(default=0, ge=0)
    estimated_duration: int = Field(..., gt=0, description="Duration in minutes")
    due_date: Optional[date] = None
    okr_id: Optional[uuid.UUID] = None
    carried_forward: bool = False

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[TaskStatus] = None
    rank: Optional[int] = None
    estimated_duration: Optional[int] = None
    due_date: Optional[date] = None
    okr_id: Optional[uuid.UUID] = None

class TaskResponse(TaskBase):
    id: uuid.UUID
    user_id: uuid.UUID
    memory_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class DraftTaskResponse(TaskResponse):
    generation_context: Optional[Dict[str, Any]] = None

# Daily Brief Models
class DailyBriefGenerateRequest(BaseModel):
    force_regenerate: bool = False
    include_context: Optional[str] = None

class DailyBriefApprovalRequest(BaseModel):
    task_ids: List[uuid.UUID]
    modifications: Optional[Dict[uuid.UUID, Dict[str, Any]]] = None

class DailyBriefResponse(BaseModel):
    tasks: List[DraftTaskResponse]
    generation_context: Dict[str, Any]
    generated_at: datetime
    ready_for_approval: bool

# Weekly Planning Models
class WeeklyOKRBase(BaseModel):
    objective_text: str = Field(..., max_length=1000)
    key_results: str = Field(..., max_length=2000)
    week_start_date: date

class WeeklyOKRCreate(WeeklyOKRBase):
    pass

class WeeklyOKRUpdate(BaseModel):
    objective_text: Optional[str] = None
    key_results: Optional[str] = None

class WeeklyOKRResponse(WeeklyOKRBase):
    id: uuid.UUID
    user_id: uuid.UUID
    approval_status: ApprovalStatus
    approved_at: Optional[datetime] = None
    auto_approved: bool = False
    memory_id: Optional[str] = None
    created_at: datetime

class DraftWeeklyOKRResponse(WeeklyOKRResponse):
    generation_context: Optional[Dict[str, Any]] = None

class WeeklyPlanGenerateRequest(BaseModel):
    force_regenerate: bool = False
    context_override: Optional[str] = None

class WeeklyPlanApprovalRequest(BaseModel):
    okr_ids: List[uuid.UUID]
    modifications: Optional[Dict[uuid.UUID, Dict[str, Any]]] = None

# Analytics Models
class MemoryInsightsResponse(BaseModel):
    task_completions: int
    productive_time: str
    context_strength: str
    weekly_completion_rate: float
    estimated_vs_actual_time: Dict[str, Any]

class LLMUsageResponse(BaseModel):
    total_tokens: int
    cost_estimate: float
    requests_count: int
    memory_context_usage: int

# API Response Models
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
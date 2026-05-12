from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any

# --- Tasks ---

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = ""
    due_date: Optional[str] = None
    duration: int = 30
    status: str = "backlog"
    scheduled_time: Optional[str] = None
    scheduled_date: Optional[str] = None
    is_completed: bool = False

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[str] = None
    duration: Optional[int] = None
    scheduled_time: Optional[str] = None
    scheduled_date: Optional[str] = None
    is_completed: Optional[bool] = None

class TaskResponse(TaskBase):
    id: str
    status: str
    created_at: str
    updated_at: str
    content: Optional[str] = ""

class TaskMoveRequest(BaseModel):
    target_status: str # backlog | today | scheduled
    scheduled_time: Optional[str] = None
    scheduled_date: Optional[str] = None

# --- Daily Logs ---

class LogDayRequest(BaseModel):
    date_to_log: Optional[str] = None

class DailyLogCreate(BaseModel):
    total_tasks: int
    completed_tasks: int
    completion_pct: float
    content: Optional[str] = ""

class DailyLogResponse(DailyLogCreate):
    date: str

# --- Templates ---

class TemplateUpdate(BaseModel):
    content: str # YAML list of default items as string for now

class TemplateResponse(BaseModel):
    day: str
    content: str

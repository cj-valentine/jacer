from typing import Literal

from pydantic import BaseModel, Field

from jacer.models import Cadence, TaskStatus, WeekSlot


class TaskCreate(BaseModel):
    title: str
    description: str = ""
    duration_minutes: int = 30
    status: TaskStatus = "backlog"
    category_id: str | None = None
    scheduled_time: str | None = None
    scheduled_date: str | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    duration_minutes: int | None = None
    status: TaskStatus | None = None
    category_id: str | None = None
    scheduled_time: str | None = None
    scheduled_date: str | None = None
    is_completed: bool | None = None


class TemplateCreate(BaseModel):
    name: str
    cadence: Cadence = "weekly"
    week_a_start_date: str | None = None


class TemplateUpdate(BaseModel):
    name: str | None = None
    cadence: Cadence | None = None
    week_a_start_date: str | None = None


class TemplateItemCreate(BaseModel):
    day_of_week: int = Field(ge=0, le=6)
    week_slot: WeekSlot | None = None
    title: str
    description: str = ""
    duration_minutes: int = 30
    default_time: str | None = None
    category_id: str | None = None


class TemplateItemUpdate(BaseModel):
    day_of_week: int | None = Field(default=None, ge=0, le=6)
    week_slot: WeekSlot | None = None
    title: str | None = None
    description: str | None = None
    duration_minutes: int | None = None
    default_time: str | None = None
    category_id: str | None = None


class MaterialiseResponse(BaseModel):
    date: str
    created_count: int
    created_task_ids: list[str]


class HorizonMaterialiseResponse(BaseModel):
    start_date: str
    days: int
    created_count: int
    created_task_ids: list[str]


class LockResponse(BaseModel):
    template_id: str
    is_locked: bool


class DeleteResponse(BaseModel):
    deleted: Literal[True] = True

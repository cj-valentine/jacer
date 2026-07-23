from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

TaskStatus = Literal["backlog", "today", "scheduled", "done"]
Cadence = Literal["weekly", "fortnightly"]
WeekSlot = Literal["A", "B"]


class Category(BaseModel):
    id: str
    name: str
    colour: str


# A small, fixed palette of muted tones that read well on the charcoal dark
# theme. Category colours are constrained to this set (Phase 3.5, Amendment 2):
# a category's colour is either chosen from here or auto-assigned round-robin.
CATEGORY_PALETTE: list[str] = [
    "#5B7B9A",  # slate blue
    "#6E8B6E",  # sage
    "#B07156",  # clay
    "#8A6D8B",  # plum
    "#B39154",  # ochre
    "#4F8A85",  # teal
    "#A96B76",  # rose
    "#7C8290",  # steel
]


class Task(BaseModel):
    id: str
    title: str
    description: str = ""
    duration_minutes: int = 30
    status: TaskStatus = "backlog"
    category_id: str | None = None
    scheduled_time: str | None = None
    scheduled_date: str | None = None
    is_completed: bool = False

    template_origin_id: str | None = None
    instance_date: str | None = None
    diverged: bool = False

    created_at: datetime
    updated_at: datetime


class Template(BaseModel):
    id: str
    name: str
    cadence: Cadence = "weekly"
    week_a_start_date: str | None = None
    is_locked: bool = False
    created_at: datetime
    updated_at: datetime


class TemplateItem(BaseModel):
    id: str
    template_id: str
    day_of_week: int = Field(ge=0, le=6)
    week_slot: WeekSlot | None = None
    title: str
    description: str = ""
    duration_minutes: int = 30
    default_time: str | None = None
    category_id: str | None = None


class DailyLog(BaseModel):
    date: str
    total_tasks: int = 0
    completed_tasks: int = 0
    completion_pct: float = 0.0
    content: str = ""

from fastapi import APIRouter
from typing import List
from datetime import date

from backend import schemas
from backend.services import file_io

router = APIRouter()

@router.get("/", response_model=List[schemas.TaskResponse])
def get_today_tasks():
    tasks = file_io.list_tasks()
    today_tasks = [t for t in tasks if t.get("status") == "today"]
    return today_tasks

@router.post("/populate", response_model=List[schemas.TaskResponse])
def populate_today(skip_existing: bool = True):
    # Determine today's day-of-week
    today_name = date.today().strftime('%A').lower()
    
    template = file_io.get_template(today_name)
    if not template or not template.get("content"):
        return []
        
    import yaml
    try:
        items = yaml.safe_load(template["content"])
    except yaml.YAMLError:
        return []
        
    if not items or not isinstance(items, list):
        return []

    # Get current tasks to check for duplicates if skip_existing is true
    existing_tasks = []
    if skip_existing:
        tasks = file_io.list_tasks()
        existing_tasks = [t.get("title") for t in tasks if t.get("status") in ["today", "scheduled"]]

    created_tasks = []
    
    for item in items:
        if not isinstance(item, dict) or "title" not in item:
            continue
            
        if skip_existing and item["title"] in existing_tasks:
            continue
            
        task_data = {
            "title": item["title"],
            "status": "scheduled" if item.get("scheduled_time") else "today",
            "duration": item.get("duration", 30),
            "scheduled_time": item.get("scheduled_time"),
            "scheduled_date": date.today().isoformat() if item.get("scheduled_time") else None
        }
        
        new_task = file_io.create_task(task_data)
        if new_task:
            created_tasks.append(new_task)
            
    return created_tasks

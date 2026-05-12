from fastapi import APIRouter, HTTPException
from typing import List

from backend import schemas
from backend.services import file_io

router = APIRouter()

@router.get("/{target_date}", response_model=List[schemas.TaskResponse])
def get_schedule(target_date: str):
    tasks = file_io.list_tasks()
    scheduled_tasks = [
        t for t in tasks 
        if t.get("status") == "scheduled" and t.get("scheduled_date") == target_date
    ]
    
    # Sort by time
    def _sort_key(t):
        time_str = t.get("scheduled_time") or "23:59"
        return time_str
        
    scheduled_tasks.sort(key=_sort_key)
    return scheduled_tasks

@router.put("/{task_id}", response_model=schemas.TaskResponse)
def update_schedule(task_id: str, update: schemas.TaskUpdate):
    # Only allow updating schedule-related fields
    update_data = update.model_dump(exclude_unset=True)
    
    updated = file_io.update_task(task_id, update_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated

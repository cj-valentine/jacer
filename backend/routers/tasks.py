from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from backend import schemas
from backend.services import file_io

router = APIRouter()

@router.get("/", response_model=List[schemas.TaskResponse])
def list_tasks(
    status: Optional[str] = None,
    due_before: Optional[str] = None,
    due_after: Optional[str] = None,
):
    tasks = file_io.list_tasks()
    
    # Apply filters
    if status:
        tasks = [t for t in tasks if t.get("status") == status]
    if due_before:
        tasks = [t for t in tasks if t.get("due_date") and t.get("due_date") <= due_before]
    if due_after:
        tasks = [t for t in tasks if t.get("due_date") and t.get("due_date") >= due_after]
        
    return tasks

@router.post("/", response_model=schemas.TaskResponse)
def create_task(task: schemas.TaskCreate):
    created_task = file_io.create_task(task.model_dump(exclude_unset=True))
    if not created_task:
        raise HTTPException(status_code=500, detail="Failed to create task")
    return created_task

@router.get("/{task_id}", response_model=schemas.TaskResponse)
def get_task(task_id: str):
    task = file_io.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{task_id}", response_model=schemas.TaskResponse)
def update_task(task_id: str, task: schemas.TaskUpdate):
    updated = file_io.update_task(task_id, task.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found or update failed")
    return updated

@router.delete("/{task_id}")
def delete_task(task_id: str):
    success = file_io.delete_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found or delete failed")
    return {"success": True}

@router.post("/{task_id}/move", response_model=schemas.TaskResponse)
def move_task(task_id: str, move_req: schemas.TaskMoveRequest):
    update_data = {"status": move_req.target_status}
    
    if move_req.target_status == "scheduled":
        if not move_req.scheduled_time or not move_req.scheduled_date:
            raise HTTPException(status_code=400, detail="scheduled_time and scheduled_date required when moving to scheduled")
        update_data["scheduled_time"] = move_req.scheduled_time
        update_data["scheduled_date"] = move_req.scheduled_date
    elif move_req.target_status in ["backlog", "today"]:
        # Optionally clear out scheduling data if dragged off the schedule,
        # but the spec doesn't strictly demand it. We'll leave it simple for now.
        pass

    updated = file_io.update_task(task_id, update_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated

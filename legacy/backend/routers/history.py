from fastapi import APIRouter, HTTPException
from typing import List
import os
from datetime import date

from backend import schemas
from backend.services import file_io

router = APIRouter()

@router.get("/", response_model=List[str])
def list_history():
    logs_dir = file_io.LOGS_DIR
    dates = []
    if os.path.exists(logs_dir):
        for filename in os.listdir(logs_dir):
            if filename.endswith(".md"):
                dates.append(filename[:-3])
                
    # Sort newest first
    dates.sort(reverse=True)
    return dates

@router.get("/{date}", response_model=schemas.DailyLogResponse)
def get_history(date: str):
    log = file_io.get_daily_log(date)
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    return log

@router.post("/log", response_model=schemas.DailyLogResponse)
def log_day(req: schemas.LogDayRequest = None):
    today = req.date_to_log if req and req.date_to_log else date.today().isoformat()
    tasks = file_io.list_tasks()
    
    # We only care about tasks targeting the requested log date
    relevant_tasks = [
        t for t in tasks 
        if t.get("status") == "today" or 
           (t.get("status") == "scheduled" and t.get("scheduled_date") == today)
    ]
    
    total = len(relevant_tasks)
    
    # If there are no tasks for the day, we still want to log an empty day rather than 
    # throwing an error, so the frontend can successfully "Archive and Start Day".
    if total == 0:
        log_data = {
            "content": f"# End of Day Log: {today}\nNo tasks were tracked for this day.\n",
            "total_tasks": 0,
            "completed_tasks": 0,
            "completion_pct": 0.0
        }
        success = file_io.save_daily_log(today, log_data)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to write log file.")
        return file_io.get_daily_log(today)
        
    completed_tasks = [t for t in relevant_tasks if t.get("is_completed")]
    completed_count = len(completed_tasks)
    
    pct = round((completed_count / total) * 100) if total > 0 else 0.0
    
    # Build Markdown Content
    content_lines = [f"# End of Day Log: {today}\n"]
    content_lines.append(f"**Completion Score**: {pct}%\n")
    content_lines.append(f"**Tasks Completed**: {completed_count}/{total}\n\n")
    
    if completed_tasks:
        content_lines.append("## Completed\n")
        for t in completed_tasks:
            content_lines.append(f"- [x] {t.get('title')}")
            if t.get("description"):
                content_lines.append(f"  - {t.get('description')}")
        content_lines.append("\n")
        
    unfinished_tasks = [t for t in relevant_tasks if not t.get("is_completed")]
    if unfinished_tasks:
        content_lines.append("## Unfinished\n")
        for t in unfinished_tasks:
            status = t.get("status")
            content_lines.append(f"- [ ] {t.get('title')} ({status})")
        content_lines.append("\n")
        
    log_content = "\n".join(content_lines)
    
    log_data = {
        "content": log_content,
        "total_tasks": total,
        "completed_tasks": completed_count,
        "completion_pct": pct
    }
    
    # Save Log
    success = file_io.save_daily_log(today, log_data)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to write log file.")
        
    # Archive the logged files to clear the board
    for t in relevant_tasks:
        file_io.archive_task(t["id"])
        
    return file_io.get_daily_log(today)

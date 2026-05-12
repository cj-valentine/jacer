import os
import time
import uuid
import frontmatter
from datetime import datetime, date
from typing import List, Dict, Any, Optional

# Define base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'data')
TASKS_DIR = os.path.join(DATA_DIR, 'tasks')
LOGS_DIR = os.path.join(DATA_DIR, 'logs')
TEMPLATES_DIR = os.path.join(DATA_DIR, 'templates')
ARCHIVE_DIR = os.path.join(DATA_DIR, 'archive')

# Ensure directories exist
for d in [TASKS_DIR, LOGS_DIR, TEMPLATES_DIR, ARCHIVE_DIR]:
    os.makedirs(d, exist_ok=True)

def _read_md_file(filepath: str, retries=3) -> Optional[Dict[str, Any]]:
    if not os.path.exists(filepath):
        return None
    for attempt in range(retries):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
                data = post.metadata
                data['content'] = post.content
                return data
        except Exception as e:
            if attempt == retries - 1:
                print(f"Error reading {filepath}: {e}")
                return None
            time.sleep(0.1)
    return None

def _write_md_file(filepath: str, metadata: Dict[str, Any], content: str = "", retries=3) -> bool:
    for attempt in range(retries):
        try:
            post = frontmatter.Post(content, **metadata)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(frontmatter.dumps(post))
            return True
        except Exception as e:
            if attempt == retries - 1:
                print(f"Error writing {filepath}: {e}")
                return False
            time.sleep(0.1)
    return False

# --- Tasks CRUD ---

def list_tasks() -> List[Dict[str, Any]]:
    tasks = []
    for filename in os.listdir(TASKS_DIR):
        if filename.endswith('.md'):
            filepath = os.path.join(TASKS_DIR, filename)
            task_data = _read_md_file(filepath)
            if task_data:
                # Ensure id is in the data, fallback to filename
                if 'id' not in task_data:
                     task_data['id'] = filename[:-3]
                tasks.append(task_data)
    return tasks

def get_task(task_id: str) -> Optional[Dict[str, Any]]:
    filepath = os.path.join(TASKS_DIR, f"{task_id}.md")
    return _read_md_file(filepath)

def create_task(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    task_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat() + "Z"
    
    metadata = {
        "id": task_id,
        "title": data.get("title", "New Task"),
        "description": data.get("description", ""),
        "status": data.get("status", "backlog"),
        "due_date": data.get("due_date"),
        "duration": data.get("duration", 30),
        "scheduled_time": data.get("scheduled_time"),
        "scheduled_date": data.get("scheduled_date"),
        "is_completed": data.get("is_completed", False),
        "created_at": now,
        "updated_at": now
    }
    content = data.get("content", f"# {metadata['title']}\n")
    
    filepath = os.path.join(TASKS_DIR, f"{task_id}.md")
    if _write_md_file(filepath, metadata, content):
        return get_task(task_id)
    return None

def update_task(task_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    existing = get_task(task_id)
    if not existing:
        return None
        
    content = data.pop("content", existing.pop("content", ""))
    
    # Update metadata
    for k, v in data.items():
        existing[k] = v
        
    existing["updated_at"] = datetime.utcnow().isoformat() + "Z"
    
    filepath = os.path.join(TASKS_DIR, f"{task_id}.md")
    if _write_md_file(filepath, existing, content):
        return get_task(task_id)
    return None

def delete_task(task_id: str) -> bool:
    filepath = os.path.join(TASKS_DIR, f"{task_id}.md")
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
            return True
        except Exception:
            return False
    return False

def archive_task(task_id: str) -> bool:
    filepath = os.path.join(TASKS_DIR, f"{task_id}.md")
    archive_path = os.path.join(ARCHIVE_DIR, f"{task_id}.md")
    if os.path.exists(filepath):
        try:
            os.rename(filepath, archive_path)
            return True
        except Exception:
            return False
    return False

# --- Daily Logs CRUD ---

def get_daily_log(log_date: str) -> Optional[Dict[str, Any]]:
    filepath = os.path.join(LOGS_DIR, f"{log_date}.md")
    return _read_md_file(filepath)

def save_daily_log(log_date: str, data: Dict[str, Any]) -> bool:
    content = data.pop("content", f"# Daily Log — {log_date}\n")
    metadata = {
        "date": log_date,
        "total_tasks": data.get("total_tasks", 0),
        "completed_tasks": data.get("completed_tasks", 0),
        "completion_pct": data.get("completion_pct", 0.0)
    }
    # put content back so tests don't fail when mutating dictionary
    data["content"] = content
    filepath = os.path.join(LOGS_DIR, f"{log_date}.md")
    return _write_md_file(filepath, metadata, content)

# --- Templates CRUD ---
def get_template(day: str) -> Optional[Dict[str, Any]]:
    day = day.lower()
    filepath = os.path.join(TEMPLATES_DIR, f"template-{day}.md")
    return _read_md_file(filepath)

def save_template(day: str, data: Dict[str, Any]) -> bool:
    day = day.lower()
    content = data.pop("content", "")
    metadata = {"day": day}
    data["content"] = content
    filepath = os.path.join(TEMPLATES_DIR, f"template-{day}.md")
    return _write_md_file(filepath, metadata, content)

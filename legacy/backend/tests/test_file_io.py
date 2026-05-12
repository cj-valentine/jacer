import pytest
import os
from datetime import datetime
import backend.services.file_io as file_io

def test_directories_created(test_data_dir):
    """Ensure the mock directories are created."""
    assert os.path.exists(file_io.TASKS_DIR)
    assert os.path.exists(file_io.LOGS_DIR)

def test_create_and_get_task(test_data_dir):
    data = {
        "title": "Test Task",
        "description": "A test task",
        "status": "backlog",
        "duration": 45,
        "content": "# Test Task\nBody content"
    }
    
    # Create
    created = file_io.create_task(data)
    assert created is not None
    assert created["title"] == "Test Task"
    assert "id" in created
    task_id = created["id"]
    
    # Get
    fetched = file_io.get_task(task_id)
    assert fetched is not None
    assert fetched["title"] == "Test Task"
    assert fetched["content"].strip() == "# Test Task\nBody content"
    assert fetched["duration"] == 45

def test_list_tasks(test_data_dir):
    # Create a couple of tasks
    file_io.create_task({"title": "Task 1"})
    file_io.create_task({"title": "Task 2"})
    
    tasks = file_io.list_tasks()
    assert len(tasks) == 2
    titles = [t["title"] for t in tasks]
    assert "Task 1" in titles
    assert "Task 2" in titles

def test_update_task(test_data_dir):
    created = file_io.create_task({"title": "Original"})
    task_id = created["id"]
    
    # Update title and status
    updated = file_io.update_task(task_id, {"title": "Updated", "status": "today"})
    assert updated is not None
    assert updated["title"] == "Updated"
    assert updated["status"] == "today"
    
    # Verify persistence
    fetched = file_io.get_task(task_id)
    assert fetched["title"] == "Updated"

def test_delete_task(test_data_dir):
    created = file_io.create_task({"title": "Delete Me"})
    task_id = created["id"]
    
    assert file_io.get_task(task_id) is not None
    
    # Delete
    success = file_io.delete_task(task_id)
    assert success is True
    assert file_io.get_task(task_id) is None

def test_archive_task(test_data_dir):
    created = file_io.create_task({"title": "Archive Me"})
    task_id = created["id"]
    
    # Archive
    success = file_io.archive_task(task_id)
    assert success is True
    
    # No longer in active tasks
    assert file_io.get_task(task_id) is None
    
    # Should exist in archive
    archive_path = os.path.join(file_io.ARCHIVE_DIR, f"{task_id}.md")
    assert os.path.exists(archive_path)

def test_daily_log_roundtrip(test_data_dir):
    log_date = "2024-01-01"
    data = {
        "total_tasks": 10,
        "completed_tasks": 5,
        "completion_pct": 50.0,
        "content": "# Log for 2024-01-01\n- Task A"
    }
    
    success = file_io.save_daily_log(log_date, data)
    assert success is True
    
    fetched = file_io.get_daily_log(log_date)
    assert fetched is not None
    assert fetched["total_tasks"] == 10
    assert fetched["completion_pct"] == 50.0
    assert fetched["content"].strip() == data["content"]

import pytest
import os
import backend.services.file_io as file_io

def test_history_list_empty(client, test_data_dir):
    response = client.get("/api/history/")
    assert response.status_code == 200
    assert response.json() == []

def test_history_log_day(client, test_data_dir):
    # Create some tasks to log
    # Need to simulate "today's tasks" - either status today or updated today
    t1 = file_io.create_task({"title": "Done Task", "status": "today", "is_completed": True})
    t2 = file_io.create_task({"title": "Incomplete Task", "status": "today"})
    
    # Do not log this one
    file_io.create_task({"title": "Backlog Task", "status": "backlog"})
    
    response = client.post("/api/history/log")
    
    assert response.status_code == 200
    data = response.json()
    
    # We should have aggregated the two tasks
    assert data["total_tasks"] == 2
    assert data["completed_tasks"] == 1
    assert data["completion_pct"] == 50.0  # (1/2)*100
    
    # The active tasks should be archived
    assert file_io.get_task(t1["id"]) is None
    assert file_io.get_task(t2["id"]) is None
    
    # Check history list
    list_resp = client.get("/api/history/")
    assert list_resp.status_code == 200
    logs = list_resp.json()
    assert len(logs) == 1
    assert logs[0] == data["date"]

def test_history_get_specific(client, test_data_dir):
    # Log a day to create the data
    file_io.create_task({"title": "Done", "status": "today", "is_completed": True})
    post_resp = client.post("/api/history/log")
    date_str = post_resp.json()["date"]
    
    # Fetch it
    get_resp = client.get(f"/api/history/{date_str}")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["date"] == date_str
    assert data["total_tasks"] == 1
    assert data["completed_tasks"] == 1
    assert "Done" in data["content"]

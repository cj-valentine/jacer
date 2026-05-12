import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Jacer API is running"}

def test_create_and_read_task():
    # Create
    new_task = {
        "title": "API Test Task",
        "description": "Created via API test",
        "duration": 45
    }
    response = client.post("/api/tasks/", json=new_task)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "API Test Task"
    assert "id" in data
    task_id = data["id"]
    
    # Read
    response = client.get(f"/api/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "API Test Task"
    
    # Update
    update_data = {"status": "today"}
    response = client.put(f"/api/tasks/{task_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["status"] == "today"
    
    # Delete
    response = client.delete(f"/api/tasks/{task_id}")
    assert response.status_code == 200
    
    # Verify deletion
    response = client.get(f"/api/tasks/{task_id}")
    assert response.status_code == 404

def test_move_task():
    new_task = {"title": "Move Test"}
    response = client.post("/api/tasks/", json=new_task)
    task_id = response.json()["id"]
    
    # Move to scheduled
    move_req = {
        "target_status": "scheduled",
        "scheduled_time": "14:00",
        "scheduled_date": "2026-03-10"
    }
    response = client.post(f"/api/tasks/{task_id}/move", json=move_req)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "scheduled"
    assert data["scheduled_time"] == "14:00"
    
    client.delete(f"/api/tasks/{task_id}")

def test_today_list():
    response = client.get("/api/today/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_templates_list():
    response = client.get("/api/templates/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_history_list():
    response = client.get("/api/history/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

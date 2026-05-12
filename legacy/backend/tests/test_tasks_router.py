import pytest

def test_tasks_list_empty(client, test_data_dir):
    response = client.get("/api/tasks/")
    assert response.status_code == 200
    assert response.json() == []

def test_tasks_create_and_get(client, test_data_dir):
    # Create
    payload = {
        "title": "API Task",
        "description": "Created via TEST API",
        "status": "backlog",
        "duration": 60
    }
    create_resp = client.post("/api/tasks/", json=payload)
    assert create_resp.status_code == 200
    created = create_resp.json()
    assert "id" in created
    assert created["title"] == "API Task"
    
    task_id = created["id"]
    
    # Get List
    list_resp = client.get("/api/tasks/")
    assert list_resp.status_code == 200
    tasks = list_resp.json()
    assert len(tasks) == 1
    assert tasks[0]["id"] == task_id
    
    # Get Single
    get_resp = client.get(f"/api/tasks/{task_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == task_id

def test_tasks_update(client, test_data_dir):
    # Setup
    created = client.post("/api/tasks/", json={"title": "To Update"}).json()
    task_id = created["id"]
    
    # Update
    update_payload = {"status": "today", "title": "Updated Title"}
    update_resp = client.put(f"/api/tasks/{task_id}", json=update_payload)
    
    assert update_resp.status_code == 200
    updated = update_resp.json()
    assert updated["status"] == "today"
    assert updated["title"] == "Updated Title"

def test_tasks_move(client, test_data_dir):
    # Setup
    created = client.post("/api/tasks/", json={"title": "To Move"}).json()
    task_id = created["id"]
    
    # Move
    move_payload = {"target_status": "today"}
    move_resp = client.post(f"/api/tasks/{task_id}/move", json=move_payload)
    
    assert move_resp.status_code == 200
    moved = move_resp.json()
    assert moved["status"] == "today"

def test_tasks_delete(client, test_data_dir):
    # Setup
    created = client.post("/api/tasks/", json={"title": "To Delete"}).json()
    task_id = created["id"]
    
    # Delete
    del_resp = client.delete(f"/api/tasks/{task_id}")
    assert del_resp.status_code == 200
    assert del_resp.json() == {"success": True}
    
    # Verify Gone
    get_resp = client.get(f"/api/tasks/{task_id}")
    assert get_resp.status_code == 404

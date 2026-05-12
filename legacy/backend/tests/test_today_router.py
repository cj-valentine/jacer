import pytest
import os
import backend.services.file_io as file_io

def test_today_get_empty(client, test_data_dir):
    response = client.get("/api/today/")
    assert response.status_code == 200
    assert response.json() == []

def test_today_get_tasks(client, test_data_dir):
    # Setup some test tasks
    file_io.create_task({"title": "In Backlog", "status": "backlog"})
    file_io.create_task({"title": "In Today", "status": "today"})
    
    response = client.get("/api/today/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "In Today"

def test_today_populate(client, test_data_dir):
    # Setup a template for the test
    # We don't mock the date here easily without monkeypatch, 
    # but we can just use the endpoint and assert it responds correctly
    
    # Just to be safe, create a template for 'monday' through 'sunday'
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    for day in days:
        file_io.save_template(day, {"content": "- title: Populated Task"})
        
    response = client.post("/api/today/populate?skip_existing=true")
    assert response.status_code == 200
    data = response.json()
    
    # At least one task should be created
    assert len(data) > 0
    assert data[0]["title"] == "Populated Task"
    assert data[0]["status"] == "today"

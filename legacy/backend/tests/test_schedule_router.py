import pytest
import datetime
import backend.services.file_io as file_io

def test_schedule_get_empty(client, test_data_dir):
    response = client.get("/api/schedule/2024-01-01")
    assert response.status_code == 200
    assert response.json() == []

def test_schedule_get_tasks(client, test_data_dir):
    # Setup
    target_date = "2024-01-01"
    file_io.create_task({
        "title": "Scheduled A",
        "status": "scheduled",
        "scheduled_date": target_date
    })
    
    file_io.create_task({
        "title": "Scheduled B",
        "status": "scheduled",
        "scheduled_date": "2024-12-31" # different date
    })
    
    file_io.create_task({
        "title": "Today Task",
        "status": "today" # different status
    })
    
    response = client.get(f"/api/schedule/{target_date}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Scheduled A"

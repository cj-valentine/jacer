import pytest

def test_templates_init(client, test_data_dir):
    # Initialize templates
    from backend.routers.templates import DAYS
    import backend.services.file_io as file_io
    for day in DAYS:
        file_io.save_template(day, {"content": ""})

    response = client.get("/api/templates/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 7
    # They should all be initialized with empty string content
    for item in data:
        assert item["content"] == ""

def test_template_update(client, test_data_dir):
    payload = {"content": "- [ ] Buy Groceries"}
    response = client.put("/api/templates/monday", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["day"] == "monday"
    assert data["content"] == "- [ ] Buy Groceries"
    
    # Refetch
    get_response = client.get("/api/templates/")
    data2 = get_response.json()
    monday_template = next(d for d in data2 if d["day"] == "monday")
    assert monday_template["content"] == "- [ ] Buy Groceries"

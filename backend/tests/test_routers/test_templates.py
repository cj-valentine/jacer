def test_create_weekly_template(client):
    response = client.post("/api/templates/", json={"name": "Weekly routine"})
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Weekly routine"
    assert body["cadence"] == "weekly"
    assert body["is_locked"] is False


def test_create_fortnightly_template_requires_reference_date(client):
    response = client.post(
        "/api/templates/",
        json={"name": "Fortnightly", "cadence": "fortnightly"},
    )
    assert response.status_code == 422
    assert "week_a_start_date" in response.json()["detail"]


def test_create_fortnightly_template(client):
    response = client.post(
        "/api/templates/",
        json={
            "name": "Fortnightly",
            "cadence": "fortnightly",
            "week_a_start_date": "2026-05-11",
        },
    )
    assert response.status_code == 201
    assert response.json()["cadence"] == "fortnightly"


def test_list_templates(client):
    client.post("/api/templates/", json={"name": "A"})
    client.post("/api/templates/", json={"name": "B"})
    response = client.get("/api/templates/")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_update_template(client):
    created = client.post("/api/templates/", json={"name": "Old"}).json()
    response = client.patch(f"/api/templates/{created['id']}", json={"name": "New"})
    assert response.status_code == 200
    assert response.json()["name"] == "New"


def test_delete_template(client):
    created = client.post("/api/templates/", json={"name": "Disposable"}).json()
    assert client.delete(f"/api/templates/{created['id']}").status_code == 200
    assert client.get(f"/api/templates/{created['id']}").status_code == 404


def test_lock_template(client):
    created = client.post("/api/templates/", json={"name": "Routine"}).json()
    response = client.post(f"/api/templates/{created['id']}/lock")
    assert response.status_code == 200
    assert response.json()["is_locked"] is True
    assert client.get(f"/api/templates/{created['id']}").json()["is_locked"] is True


def test_unlock_template(client):
    created = client.post("/api/templates/", json={"name": "Routine"}).json()
    client.post(f"/api/templates/{created['id']}/lock")
    response = client.post(f"/api/templates/{created['id']}/unlock")
    assert response.status_code == 200
    assert response.json()["is_locked"] is False


def test_lock_template_not_found(client):
    response = client.post("/api/templates/nope/lock")
    assert response.status_code == 404

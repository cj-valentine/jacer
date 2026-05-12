import pytest


@pytest.fixture
def template(client):
    return client.post("/api/templates/", json={"name": "Weekly"}).json()


@pytest.fixture
def fortnightly_template(client):
    return client.post(
        "/api/templates/",
        json={
            "name": "Fortnightly",
            "cadence": "fortnightly",
            "week_a_start_date": "2026-05-11",
        },
    ).json()


def test_create_item(client, template):
    response = client.post(
        f"/api/templates/{template['id']}/items",
        json={"day_of_week": 0, "title": "Standup"},
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Standup"
    assert response.json()["template_id"] == template["id"]


def test_create_item_rejects_week_slot_on_weekly_template(client, template):
    response = client.post(
        f"/api/templates/{template['id']}/items",
        json={"day_of_week": 0, "title": "X", "week_slot": "A"},
    )
    assert response.status_code == 422


def test_create_item_accepts_week_slot_on_fortnightly_template(client, fortnightly_template):
    response = client.post(
        f"/api/templates/{fortnightly_template['id']}/items",
        json={"day_of_week": 0, "title": "Week A standup", "week_slot": "A"},
    )
    assert response.status_code == 201


def test_create_item_on_missing_template_404s(client):
    response = client.post(
        "/api/templates/missing/items",
        json={"day_of_week": 0, "title": "X"},
    )
    assert response.status_code == 404


def test_list_items(client, template):
    client.post(
        f"/api/templates/{template['id']}/items",
        json={"day_of_week": 0, "title": "Monday"},
    )
    client.post(
        f"/api/templates/{template['id']}/items",
        json={"day_of_week": 2, "title": "Wednesday"},
    )
    response = client.get(f"/api/templates/{template['id']}/items")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_update_item(client, template):
    created = client.post(
        f"/api/templates/{template['id']}/items",
        json={"day_of_week": 0, "title": "Old"},
    ).json()
    response = client.patch(
        f"/api/template-items/{created['id']}",
        json={"title": "New", "duration_minutes": 60},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "New"
    assert response.json()["duration_minutes"] == 60


def test_delete_item(client, template):
    created = client.post(
        f"/api/templates/{template['id']}/items",
        json={"day_of_week": 0, "title": "X"},
    ).json()
    assert client.delete(f"/api/template-items/{created['id']}").status_code == 200
    assert client.get(f"/api/template-items/{created['id']}").status_code == 404

def test_invalid_date_format_returns_422(client):
    response = client.get("/api/days/not-a-date")
    assert response.status_code == 422


def test_list_day_tasks_empty(client):
    response = client.get("/api/days/2026-05-13")
    assert response.status_code == 200
    assert response.json() == []


def test_list_day_tasks_returns_scheduled_and_instances(client):
    client.post(
        "/api/tasks/",
        json={"title": "Scheduled", "scheduled_date": "2026-05-13"},
    )
    client.post(
        "/api/tasks/",
        json={"title": "Other day", "scheduled_date": "2026-05-14"},
    )
    response = client.get("/api/days/2026-05-13")
    assert response.status_code == 200
    assert len(response.json()) == 1


def _make_locked_weekly_template_with_monday_item(client):
    template = client.post("/api/templates/", json={"name": "Weekly"}).json()
    client.post(
        f"/api/templates/{template['id']}/items",
        json={"day_of_week": 0, "title": "Standup", "duration_minutes": 15},
    )
    client.post(f"/api/templates/{template['id']}/lock")
    return template


def test_materialise_day_creates_tasks_for_locked_template(client):
    _make_locked_weekly_template_with_monday_item(client)

    # 2026-05-11 is a Monday (weekday=0)
    response = client.post("/api/days/2026-05-11/materialise")
    assert response.status_code == 200
    assert response.json()["created_count"] == 1

    tasks = client.get("/api/days/2026-05-11").json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Standup"
    assert tasks[0]["instance_date"] == "2026-05-11"


def test_materialise_is_idempotent(client):
    _make_locked_weekly_template_with_monday_item(client)
    first = client.post("/api/days/2026-05-11/materialise").json()
    second = client.post("/api/days/2026-05-11/materialise").json()
    assert first["created_count"] == 1
    assert second["created_count"] == 0


def test_materialise_skips_unlocked_templates(client):
    template = client.post("/api/templates/", json={"name": "Weekly"}).json()
    client.post(
        f"/api/templates/{template['id']}/items",
        json={"day_of_week": 0, "title": "Standup"},
    )
    # Template not locked

    response = client.post("/api/days/2026-05-11/materialise")
    assert response.json()["created_count"] == 0


def test_materialise_skips_non_matching_days(client):
    _make_locked_weekly_template_with_monday_item(client)

    # 2026-05-12 is a Tuesday (weekday=1)
    response = client.post("/api/days/2026-05-12/materialise")
    assert response.json()["created_count"] == 0


def test_horizon_materialisation(client):
    _make_locked_weekly_template_with_monday_item(client)
    # 14 days from a Monday includes two Mondays
    response = client.post("/api/days/horizon/materialise?start=2026-05-11&days=14")
    assert response.status_code == 200
    assert response.json()["created_count"] == 2

def test_create_task(client):
    response = client.post("/api/tasks/", json={"title": "Write report"})
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Write report"
    assert body["status"] == "backlog"
    assert body["duration_minutes"] == 30
    assert body["id"]


def test_create_task_with_all_fields(client):
    response = client.post(
        "/api/tasks/",
        json={
            "title": "Deep work block",
            "description": "Focus on the migration script",
            "duration_minutes": 90,
            "status": "scheduled",
            "scheduled_time": "09:30",
            "scheduled_date": "2026-05-13",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["duration_minutes"] == 90
    assert body["scheduled_time"] == "09:30"


def test_list_tasks(client):
    client.post("/api/tasks/", json={"title": "A"})
    client.post("/api/tasks/", json={"title": "B", "status": "today"})
    response = client.get("/api/tasks/")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_list_tasks_filtered_by_status(client):
    client.post("/api/tasks/", json={"title": "A"})  # backlog
    client.post("/api/tasks/", json={"title": "B", "status": "today"})
    response = client.get("/api/tasks/?status=today")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "B"


def test_get_task(client):
    created = client.post("/api/tasks/", json={"title": "X"}).json()
    response = client.get(f"/api/tasks/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_task_not_found(client):
    response = client.get("/api/tasks/does-not-exist")
    assert response.status_code == 404


def test_update_task(client):
    created = client.post("/api/tasks/", json={"title": "Original"}).json()
    response = client.patch(
        f"/api/tasks/{created['id']}",
        json={"title": "Renamed", "status": "today"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Renamed"
    assert response.json()["status"] == "today"


def test_update_task_not_found(client):
    response = client.patch("/api/tasks/missing", json={"title": "X"})
    assert response.status_code == 404


def test_update_task_marks_diverged_for_template_instance(client, memory_repository):
    """A user edit to a templated task must set diverged=True."""
    from datetime import UTC, datetime

    from jacer.models import Task

    now = datetime.now(UTC)
    memory_repository.save_task(
        Task(
            id="t1",
            title="Standup",
            template_origin_id="item1",
            instance_date="2026-05-13",
            created_at=now,
            updated_at=now,
        )
    )

    response = client.patch("/api/tasks/t1", json={"title": "Standup (custom)"})
    assert response.status_code == 200
    assert response.json()["diverged"] is True


def test_delete_task(client):
    created = client.post("/api/tasks/", json={"title": "Disposable"}).json()
    response = client.delete(f"/api/tasks/{created['id']}")
    assert response.status_code == 200
    assert client.get(f"/api/tasks/{created['id']}").status_code == 404


def test_delete_task_not_found(client):
    response = client.delete("/api/tasks/nope")
    assert response.status_code == 404

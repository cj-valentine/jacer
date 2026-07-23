"""ADR-006 contract: POST /api/tasks/{id}/reset-to-template.

Restores a task's definition (title, duration, category, scheduled_time) from
its originating template item and clears diverged, without touching status,
is_completed, scheduled_date or instance_date. Additive endpoint — a reset
can't be done via PATCH because PATCH re-sets diverged=True.

Runs against both repository adapters via `both_repos_client`.
"""

from datetime import UTC, datetime

from jacer.models import Task, TemplateItem


def _now() -> datetime:
    return datetime.now(UTC)


def _seed_item_and_task(repo, *, diverged=True, scheduled_date="2026-07-20"):
    repo.save_template_item(
        TemplateItem(
            id="item1",
            template_id="tpl1",
            day_of_week=0,
            title="Standup",
            duration_minutes=15,
            default_time="09:00",
            category_id="cat-work",
        )
    )
    repo.save_task(
        Task(
            id="task1",
            title="Standup (edited)",
            duration_minutes=45,
            category_id="cat-other",
            scheduled_time="11:30",
            status="today",
            is_completed=False,
            scheduled_date=scheduled_date,
            instance_date=scheduled_date,
            template_origin_id="item1",
            diverged=diverged,
            created_at=_now(),
            updated_at=_now(),
        )
    )


def test_reset_restores_definition_and_clears_diverged(both_repos_client, repository):
    _seed_item_and_task(repository)
    resp = both_repos_client.post("/api/tasks/task1/reset-to-template")
    assert resp.status_code == 200
    body = resp.json()
    # Definition restored from the item.
    assert body["title"] == "Standup"
    assert body["duration_minutes"] == 15
    assert body["category_id"] == "cat-work"
    assert body["scheduled_time"] == "09:00"
    # Diverged cleared.
    assert body["diverged"] is False


def test_reset_does_not_touch_placement_or_completion(both_repos_client, repository):
    _seed_item_and_task(repository)
    resp = both_repos_client.post("/api/tasks/task1/reset-to-template")
    body = resp.json()
    # Placement and completion are untouched.
    assert body["status"] == "today"
    assert body["is_completed"] is False
    assert body["scheduled_date"] == "2026-07-20"
    assert body["instance_date"] == "2026-07-20"


def test_reset_unknown_task_404(both_repos_client):
    resp = both_repos_client.post("/api/tasks/nope/reset-to-template")
    assert resp.status_code == 404


def test_reset_non_template_task_409(both_repos_client, repository):
    repository.save_task(Task(id="manual1", title="Manual", created_at=_now(), updated_at=_now()))
    resp = both_repos_client.post("/api/tasks/manual1/reset-to-template")
    assert resp.status_code == 409


def test_reset_missing_item_404(both_repos_client, repository):
    # Task points at a template item that no longer exists.
    repository.save_task(
        Task(
            id="orphan1",
            title="Orphan",
            template_origin_id="ghost-item",
            diverged=True,
            created_at=_now(),
            updated_at=_now(),
        )
    )
    resp = both_repos_client.post("/api/tasks/orphan1/reset-to-template")
    assert resp.status_code == 404

"""ADR-004 contract: status and is_completed are two views of one truth.

status is canonical; is_completed is derived from it. A caller may drive
either field and the pair is never left inconsistent. Every case runs against
both repository adapters via the `both_repos_client` fixture so the derived
field is proven to survive a persistence round-trip.
"""


def _create(client, **fields):
    return client.post("/api/tasks/", json={"title": "T", **fields}).json()


# Create path


def test_create_backlog_is_not_completed(both_repos_client):
    body = _create(both_repos_client)
    assert body["status"] == "backlog"
    assert body["is_completed"] is False


def test_create_done_is_completed(both_repos_client):
    body = _create(both_repos_client, status="done")
    assert body["status"] == "done"
    assert body["is_completed"] is True


# status -> is_completed


def test_patch_status_done_sets_completed(both_repos_client):
    task = _create(both_repos_client)
    body = both_repos_client.patch(f"/api/tasks/{task['id']}", json={"status": "done"}).json()
    assert body["status"] == "done"
    assert body["is_completed"] is True


def test_patch_status_away_from_done_clears_completed(both_repos_client):
    task = _create(both_repos_client, status="done")
    assert task["is_completed"] is True
    body = both_repos_client.patch(f"/api/tasks/{task['id']}", json={"status": "today"}).json()
    assert body["status"] == "today"
    assert body["is_completed"] is False


# is_completed -> status


def test_patch_completed_true_sets_status_done(both_repos_client):
    task = _create(both_repos_client, status="today")
    body = both_repos_client.patch(f"/api/tasks/{task['id']}", json={"is_completed": True}).json()
    assert body["is_completed"] is True
    assert body["status"] == "done"


def test_patch_completed_false_falls_back_to_backlog(both_repos_client):
    task = _create(both_repos_client, status="done")
    body = both_repos_client.patch(f"/api/tasks/{task['id']}", json={"is_completed": False}).json()
    assert body["is_completed"] is False
    assert body["status"] == "backlog"


# Both supplied -> status is canonical


def test_patch_both_status_wins_over_completed(both_repos_client):
    """When a PATCH carries both, status is canonical and is_completed is
    re-derived from it — even if the two disagree in the payload."""
    task = _create(both_repos_client)
    body = both_repos_client.patch(
        f"/api/tasks/{task['id']}",
        json={"status": "today", "is_completed": True},
    ).json()
    assert body["status"] == "today"
    assert body["is_completed"] is False


def test_patch_both_status_done_completed_false(both_repos_client):
    task = _create(both_repos_client)
    body = both_repos_client.patch(
        f"/api/tasks/{task['id']}",
        json={"status": "done", "is_completed": False},
    ).json()
    assert body["status"] == "done"
    assert body["is_completed"] is True


# Unrelated PATCH preserves the invariant


def test_patch_title_only_preserves_completion(both_repos_client):
    task = _create(both_repos_client, status="done")
    body = both_repos_client.patch(f"/api/tasks/{task['id']}", json={"title": "Renamed"}).json()
    assert body["title"] == "Renamed"
    assert body["status"] == "done"
    assert body["is_completed"] is True

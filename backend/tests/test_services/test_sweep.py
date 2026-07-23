"""Tests for the stale-day sweep and the ADR-005 daily-log format.

The sweep rolls past template-origin tasks into their day's log (frontmatter
stats + Obsidian-native body) and removes them from the store. Manual tasks are
never touched.
"""

from datetime import UTC, date, datetime

from jacer.models import Task
from jacer.repositories.memory import InMemoryRepository
from jacer.services.materialise import sweep_stale_days

TODAY = date(2026, 7, 24)


def _now() -> datetime:
    return datetime.now(UTC)


def _task(task_id, **fields):
    base = dict(
        id=task_id,
        title="T",
        template_origin_id="item1",
        created_at=_now(),
        updated_at=_now(),
    )
    base.update(fields)
    return Task(**base)


def test_sweeps_past_incomplete_template_task():
    repo = InMemoryRepository()
    repo.save_task(
        _task(
            "t1", title="Standup", duration_minutes=15, scheduled_date="2026-07-20", status="today"
        )
    )

    swept = sweep_stale_days(repo, TODAY)

    assert swept == ["2026-07-20"]
    assert repo.get_task("t1") is None  # removed from the board
    log = repo.get_daily_log("2026-07-20")
    assert log is not None
    assert "# 2026-07-20" in log.content
    assert "- [ ] Standup (15m)" in log.content
    assert log.total_tasks == 1
    assert log.completed_tasks == 0


def test_completed_past_task_logged_as_checked():
    repo = InMemoryRepository()
    repo.save_task(
        _task(
            "t1",
            title="Deep work",
            duration_minutes=90,
            category_id="focus",
            scheduled_date="2026-07-20",
            status="done",
            is_completed=True,
        )
    )

    sweep_stale_days(repo, TODAY)

    log = repo.get_daily_log("2026-07-20")
    assert "- [x] Deep work (90m) #focus" in log.content
    assert log.completed_tasks == 1
    assert log.completion_pct == 100.0


def test_manual_tasks_never_swept():
    repo = InMemoryRepository()
    repo.save_task(_task("manual", template_origin_id=None, scheduled_date="2026-07-20"))

    swept = sweep_stale_days(repo, TODAY)

    assert swept == []
    assert repo.get_task("manual") is not None
    assert repo.get_daily_log("2026-07-20") is None


def test_today_and_future_tasks_not_swept():
    repo = InMemoryRepository()
    repo.save_task(_task("today", scheduled_date="2026-07-24"))
    repo.save_task(_task("future", scheduled_date="2026-08-01"))

    swept = sweep_stale_days(repo, TODAY)

    assert swept == []
    assert repo.get_task("today") is not None
    assert repo.get_task("future") is not None


def test_bumped_task_not_swept_by_original_instance_date():
    """A task bumped forward keeps a past instance_date but a future
    scheduled_date; placement is scheduled_date, so it is NOT stale."""
    repo = InMemoryRepository()
    repo.save_task(_task("bumped", instance_date="2026-07-20", scheduled_date="2026-07-30"))

    swept = sweep_stale_days(repo, TODAY)

    assert swept == []
    assert repo.get_task("bumped") is not None


def test_sweep_is_idempotent():
    repo = InMemoryRepository()
    repo.save_task(_task("t1", title="A", scheduled_date="2026-07-20", status="today"))

    first = sweep_stale_days(repo, TODAY)
    second = sweep_stale_days(repo, TODAY)

    assert first == ["2026-07-20"]
    assert second == []  # nothing left to sweep
    log = repo.get_daily_log("2026-07-20")
    assert log.total_tasks == 1  # not double-counted


def test_line_omits_duration_when_zero_and_tag_when_absent():
    repo = InMemoryRepository()
    repo.save_task(
        _task("t1", title="Bare", duration_minutes=0, scheduled_date="2026-07-20", status="today")
    )

    sweep_stale_days(repo, TODAY)

    log = repo.get_daily_log("2026-07-20")
    assert "- [ ] Bare\n" in log.content
    assert "(0m)" not in log.content
    assert " #" not in log.content  # no category tag (the leading "# date" heading is fine)

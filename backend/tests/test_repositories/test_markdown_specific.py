"""Markdown-adapter-specific tests.

The shared contract tests (test_contract.py) run against every adapter and
verify the *behaviour* of the interface. This module verifies things only
the MarkdownRepository should be responsible for: file layout, persistence
across instances, atomic writes, and resilience to corrupted files.
"""

from datetime import UTC, datetime

import pytest

from jacer.models import DailyLog, Task, Template, TemplateItem
from jacer.repositories.markdown import MarkdownRepository


def _now() -> datetime:
    return datetime.now(UTC)


@pytest.fixture
def repo(tmp_path):
    return MarkdownRepository(tmp_path / "data")


def test_persistence_across_instances(tmp_path):
    """Data written by one instance is readable by a fresh one."""
    data_dir = tmp_path / "data"

    first = MarkdownRepository(data_dir)
    first.save_task(Task(id="t1", title="Persistent", created_at=_now(), updated_at=_now()))
    first.save_template(Template(id="tp1", name="Routine", created_at=_now(), updated_at=_now()))
    first.save_template_item(
        TemplateItem(id="i1", template_id="tp1", day_of_week=0, title="Standup")
    )
    first.save_daily_log(DailyLog(date="2026-05-13", total_tasks=3, completed_tasks=2))
    first.mark_materialised("tp1", "2026-05-13")

    second = MarkdownRepository(data_dir)
    assert second.get_task("t1") is not None
    assert second.get_template("tp1") is not None
    assert len(second.list_template_items("tp1")) == 1
    assert second.get_daily_log("2026-05-13") is not None
    assert second.is_materialised("tp1", "2026-05-13") is True


def test_file_layout_matches_expectations(repo, tmp_path):
    data_dir = tmp_path / "data"
    repo.save_task(Task(id="t1", title="A", created_at=_now(), updated_at=_now()))
    repo.save_template(Template(id="tp1", name="A", created_at=_now(), updated_at=_now()))
    repo.save_template_item(TemplateItem(id="i1", template_id="tp1", day_of_week=0, title="X"))
    repo.save_daily_log(DailyLog(date="2026-05-13"))
    repo.mark_materialised("tp1", "2026-05-13")

    assert (data_dir / "tasks" / "t1.md").exists()
    assert (data_dir / "templates" / "tp1.md").exists()
    assert (data_dir / "template-items" / "i1.md").exists()
    assert (data_dir / "logs" / "2026-05-13.md").exists()
    assert (data_dir / "_materialised.json").exists()


def test_task_description_round_trips_through_body(repo):
    task = Task(
        id="t1",
        title="With description",
        description="Multi-line\ndescription with **markdown**.",
        created_at=_now(),
        updated_at=_now(),
    )
    repo.save_task(task)
    fetched = repo.get_task("t1")
    assert fetched is not None
    assert fetched.description == "Multi-line\ndescription with **markdown**."


def test_corrupted_task_file_is_skipped_not_crashed(repo, tmp_path):
    repo.save_task(Task(id="t1", title="Good", created_at=_now(), updated_at=_now()))

    bad = tmp_path / "data" / "tasks" / "t2.md"
    bad.write_text("this is not valid frontmatter at all {{{{", encoding="utf-8")

    tasks = repo.list_tasks()
    assert len(tasks) == 1
    assert tasks[0].id == "t1"


def test_corrupted_materialised_index_returns_empty(repo, tmp_path):
    (tmp_path / "data" / "_materialised.json").write_text("not json {{", encoding="utf-8")
    assert repo.is_materialised("any", "2026-05-13") is False


def test_atomic_write_leaves_no_temp_files(repo, tmp_path):
    repo.save_task(Task(id="t1", title="A", created_at=_now(), updated_at=_now()))
    tasks_dir = tmp_path / "data" / "tasks"
    temp_files = list(tasks_dir.glob("*.tmp"))
    assert temp_files == []


def test_materialised_index_is_sorted_and_pretty(repo, tmp_path):
    repo.mark_materialised("tp1", "2026-05-14")
    repo.mark_materialised("tp1", "2026-05-13")
    repo.mark_materialised("tp2", "2026-05-13")

    content = (tmp_path / "data" / "_materialised.json").read_text(encoding="utf-8")
    assert "\n  " in content  # pretty-printed
    assert content.index('"tp1"') < content.index('"tp2"')  # sorted


def test_get_unknown_task_returns_none(repo):
    assert repo.get_task("does-not-exist") is None


def test_get_unknown_daily_log_returns_none(repo):
    assert repo.get_daily_log("2099-01-01") is None

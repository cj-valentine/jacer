"""Contract tests for the Repository interface.

Every concrete adapter must pass these tests. Chunk 1 exercises
InMemoryRepository only; Chunk 2 parametrises this module against
MarkdownRepository as well.
"""

from datetime import UTC, datetime

from jacer.models import DailyLog, Task, Template, TemplateItem


def _now() -> datetime:
    return datetime.now(UTC)


# Tasks


def test_save_and_get_task(repository):
    task = Task(id="t1", title="Test", created_at=_now(), updated_at=_now())
    repository.save_task(task)

    fetched = repository.get_task("t1")
    assert fetched is not None
    assert fetched.title == "Test"
    assert fetched.status == "backlog"


def test_get_unknown_task_returns_none(repository):
    assert repository.get_task("nope") is None


def test_save_task_overwrites_existing(repository):
    repository.save_task(Task(id="t1", title="First", created_at=_now(), updated_at=_now()))
    repository.save_task(Task(id="t1", title="Second", created_at=_now(), updated_at=_now()))

    fetched = repository.get_task("t1")
    assert fetched is not None
    assert fetched.title == "Second"


def test_list_tasks_filters_by_status(repository):
    repository.save_task(
        Task(id="t1", title="A", status="backlog", created_at=_now(), updated_at=_now())
    )
    repository.save_task(
        Task(id="t2", title="B", status="today", created_at=_now(), updated_at=_now())
    )
    repository.save_task(
        Task(id="t3", title="C", status="today", created_at=_now(), updated_at=_now())
    )

    assert len(repository.list_tasks(status="backlog")) == 1
    assert len(repository.list_tasks(status="today")) == 2
    assert len(repository.list_tasks(status="done")) == 0
    assert len(repository.list_tasks()) == 3


def test_list_tasks_filters_by_date(repository):
    repository.save_task(
        Task(
            id="t1",
            title="A",
            scheduled_date="2026-05-13",
            created_at=_now(),
            updated_at=_now(),
        )
    )
    repository.save_task(
        Task(
            id="t2",
            title="B",
            instance_date="2026-05-13",
            created_at=_now(),
            updated_at=_now(),
        )
    )
    repository.save_task(
        Task(
            id="t3",
            title="C",
            scheduled_date="2026-05-14",
            created_at=_now(),
            updated_at=_now(),
        )
    )

    matches = repository.list_tasks(date="2026-05-13")
    assert {t.id for t in matches} == {"t1", "t2"}


def test_delete_task(repository):
    repository.save_task(Task(id="t1", title="A", created_at=_now(), updated_at=_now()))
    assert repository.delete_task("t1") is True
    assert repository.get_task("t1") is None
    assert repository.delete_task("t1") is False


# Templates


def test_save_and_get_template(repository):
    template = Template(id="tp1", name="Weekly Routine", created_at=_now(), updated_at=_now())
    repository.save_template(template)

    fetched = repository.get_template("tp1")
    assert fetched is not None
    assert fetched.name == "Weekly Routine"
    assert fetched.cadence == "weekly"
    assert fetched.is_locked is False


def test_list_templates_returns_all(repository):
    repository.save_template(Template(id="a", name="A", created_at=_now(), updated_at=_now()))
    repository.save_template(Template(id="b", name="B", created_at=_now(), updated_at=_now()))
    assert len(repository.list_templates()) == 2


def test_delete_template(repository):
    repository.save_template(Template(id="tp1", name="A", created_at=_now(), updated_at=_now()))
    assert repository.delete_template("tp1") is True
    assert repository.get_template("tp1") is None


# Template items


def test_save_and_list_template_items(repository):
    repository.save_template_item(
        TemplateItem(id="i1", template_id="tp1", day_of_week=0, title="Standup")
    )
    repository.save_template_item(
        TemplateItem(id="i2", template_id="tp1", day_of_week=2, title="Deep work")
    )
    repository.save_template_item(
        TemplateItem(id="i3", template_id="tp2", day_of_week=0, title="Other template")
    )

    items = repository.list_template_items("tp1")
    assert {i.id for i in items} == {"i1", "i2"}


def test_delete_template_item(repository):
    repository.save_template_item(
        TemplateItem(id="i1", template_id="tp1", day_of_week=0, title="X")
    )
    assert repository.delete_template_item("i1") is True
    assert repository.get_template_item("i1") is None


# Daily logs


def test_save_and_get_daily_log(repository):
    log = DailyLog(date="2026-05-13", total_tasks=5, completed_tasks=3, completion_pct=60.0)
    repository.save_daily_log(log)

    fetched = repository.get_daily_log("2026-05-13")
    assert fetched is not None
    assert fetched.total_tasks == 5
    assert fetched.completed_tasks == 3


# Materialisation tracking


def test_materialisation_starts_false(repository):
    assert repository.is_materialised("tp1", "2026-05-13") is False


def test_mark_materialised_makes_it_true(repository):
    repository.mark_materialised("tp1", "2026-05-13")
    assert repository.is_materialised("tp1", "2026-05-13") is True
    assert repository.is_materialised("tp1", "2026-05-14") is False
    assert repository.is_materialised("tp2", "2026-05-13") is False

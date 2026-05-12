"""Template materialisation — turning template items into task instances.

A locked template is the user's declared intent for a recurring routine. When
a date arrives that the template has not yet produced tasks for, the
materialisation service generates one Task per matching TemplateItem and
records the (template_id, date) pair so the operation is idempotent.

Materialisation is intentionally lazy: it only runs when called. The router
layer calls it when the frontend loads, or when a specific date is opened.
"""

from datetime import UTC, date, datetime, timedelta
from uuid import uuid4

from jacer.models import Task, Template, TemplateItem
from jacer.repositories.base import Repository


def _week_slot_for(template: Template, target: date) -> str | None:
    """Return 'A' or 'B' for a fortnightly template on `target`, else None."""
    if template.cadence != "fortnightly":
        return None
    if template.week_a_start_date is None:
        return None
    week_a = date.fromisoformat(template.week_a_start_date)
    days_since = (target - week_a).days
    if days_since < 0:
        return None
    return "A" if (days_since // 7) % 2 == 0 else "B"


def _item_fires_on(item: TemplateItem, template: Template, target: date) -> bool:
    if item.day_of_week != target.weekday():
        return False
    if template.cadence == "fortnightly" and item.week_slot is not None:
        week_slot = _week_slot_for(template, target)
        if week_slot is None or item.week_slot != week_slot:
            return False
    return True


def _task_from_item(item: TemplateItem, target_date: str) -> Task:
    now = datetime.now(UTC)
    status = "scheduled" if item.default_time else "today"
    return Task(
        id=str(uuid4()),
        title=item.title,
        description=item.description,
        duration_minutes=item.duration_minutes,
        status=status,
        category_id=item.category_id,
        scheduled_time=item.default_time,
        scheduled_date=target_date,
        instance_date=target_date,
        template_origin_id=item.id,
        created_at=now,
        updated_at=now,
    )


def materialise_day(repo: Repository, target_date: str) -> list[Task]:
    """Generate task instances for `target_date` from all locked templates.

    Idempotent — a template that has already been materialised for the given
    date is skipped. Returns the list of newly-created tasks (empty if all
    locked templates were already materialised for this date).
    """
    target = date.fromisoformat(target_date)
    created: list[Task] = []

    for template in repo.list_templates():
        if not template.is_locked:
            continue
        if repo.is_materialised(template.id, target_date):
            continue

        for item in repo.list_template_items(template.id):
            if not _item_fires_on(item, template, target):
                continue
            task = _task_from_item(item, target_date)
            repo.save_task(task)
            created.append(task)

        repo.mark_materialised(template.id, target_date)

    return created


def materialise_horizon(repo: Repository, start_date: str, days: int = 14) -> list[Task]:
    """Materialise the next `days` days starting from `start_date`."""
    start = date.fromisoformat(start_date)
    created: list[Task] = []
    for offset in range(days):
        d = (start + timedelta(days=offset)).isoformat()
        created.extend(materialise_day(repo, d))
    return created

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

from jacer.models import DailyLog, Task, Template, TemplateItem
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


# ── Stale-day sweep (ADR-005) ────────────────────────────────────────────────


def _day_log_line(task: Task) -> str:
    """One Obsidian-native checkbox line for a task (ADR-005 format):

        - [x] Title (45m) #category

    The duration parens and the category tag are omitted when absent.
    """
    check = "x" if task.status == "done" else " "
    parts = [f"- [{check}] {task.title}"]
    if task.duration_minutes:
        parts.append(f"({task.duration_minutes}m)")
    if task.category_id:
        parts.append(f"#{task.category_id}")
    return " ".join(parts)


def _write_day_log(repo: Repository, log_date: str, tasks: list[Task]) -> None:
    """Record `tasks` into `log_date`'s daily log (frontmatter stats + native
    markdown body). Appends to any existing log rather than clobbering it, so a
    day swept in more than one pass accumulates rather than overwrites."""
    lines = [_day_log_line(t) for t in tasks]
    done = sum(1 for t in tasks if t.status == "done")

    existing = repo.get_daily_log(log_date)
    if existing is not None and existing.content.strip():
        body = existing.content.rstrip() + "\n" + "\n".join(lines) + "\n"
        total = existing.total_tasks + len(tasks)
        completed = existing.completed_tasks + done
    else:
        body = f"# {log_date}\n\n" + "\n".join(lines) + "\n"
        total = len(tasks)
        completed = done

    pct = round(completed / total * 100, 1) if total else 0.0
    repo.save_daily_log(
        DailyLog(
            date=log_date,
            total_tasks=total,
            completed_tasks=completed,
            completion_pct=pct,
            content=body,
        )
    )


def sweep_stale_days(repo: Repository, today: date) -> list[str]:
    """Roll past template-origin tasks into their day's log and off the board.

    A task is swept when it originated from a template (``template_origin_id``
    set) and its current placement (``scheduled_date``, falling back to
    ``instance_date``) is before ``today``. Both completed and incomplete items
    are recorded — completed as ``- [x]``, incomplete as ``- [ ]`` — then removed
    from the store. Manual tasks (no template origin) are NEVER swept.

    Returns the dates swept. Idempotent: swept tasks are deleted, so a repeat
    run finds nothing new for those days.
    """
    by_date: dict[str, list[Task]] = {}
    for task in repo.list_tasks():
        if task.template_origin_id is None:
            continue  # manual tasks are never swept
        placement = task.scheduled_date or task.instance_date
        if placement is None:
            continue
        try:
            if date.fromisoformat(placement) >= today:
                continue
        except ValueError:
            continue
        by_date.setdefault(placement, []).append(task)

    swept: list[str] = []
    for log_date in sorted(by_date):
        tasks = sorted(by_date[log_date], key=lambda t: (t.scheduled_time or "", t.title))
        _write_day_log(repo, log_date, tasks)
        for task in tasks:
            repo.delete_task(task.id)
        swept.append(log_date)
    return swept

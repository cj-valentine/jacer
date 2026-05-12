from jacer.models import DailyLog, Task, Template, TemplateItem
from jacer.repositories.base import Repository


class InMemoryRepository(Repository):
    """In-memory adapter. Used in tests and for ephemeral dev runs."""

    def __init__(self) -> None:
        self._tasks: dict[str, Task] = {}
        self._templates: dict[str, Template] = {}
        self._template_items: dict[str, TemplateItem] = {}
        self._daily_logs: dict[str, DailyLog] = {}
        self._materialised: set[tuple[str, str]] = set()

    # Tasks

    def list_tasks(
        self,
        status: str | None = None,
        date: str | None = None,
    ) -> list[Task]:
        result = list(self._tasks.values())
        if status is not None:
            result = [t for t in result if t.status == status]
        if date is not None:
            result = [
                t
                for t in result
                if t.scheduled_date == date or t.instance_date == date
            ]
        return result

    def get_task(self, task_id: str) -> Task | None:
        return self._tasks.get(task_id)

    def save_task(self, task: Task) -> Task:
        self._tasks[task.id] = task
        return task

    def delete_task(self, task_id: str) -> bool:
        return self._tasks.pop(task_id, None) is not None

    # Templates

    def list_templates(self) -> list[Template]:
        return list(self._templates.values())

    def get_template(self, template_id: str) -> Template | None:
        return self._templates.get(template_id)

    def save_template(self, template: Template) -> Template:
        self._templates[template.id] = template
        return template

    def delete_template(self, template_id: str) -> bool:
        return self._templates.pop(template_id, None) is not None

    # Template items

    def list_template_items(self, template_id: str) -> list[TemplateItem]:
        return [
            item
            for item in self._template_items.values()
            if item.template_id == template_id
        ]

    def get_template_item(self, item_id: str) -> TemplateItem | None:
        return self._template_items.get(item_id)

    def save_template_item(self, item: TemplateItem) -> TemplateItem:
        self._template_items[item.id] = item
        return item

    def delete_template_item(self, item_id: str) -> bool:
        return self._template_items.pop(item_id, None) is not None

    # Daily logs

    def get_daily_log(self, log_date: str) -> DailyLog | None:
        return self._daily_logs.get(log_date)

    def save_daily_log(self, log: DailyLog) -> DailyLog:
        self._daily_logs[log.date] = log
        return log

    # Materialisation tracking

    def is_materialised(self, template_id: str, date: str) -> bool:
        return (template_id, date) in self._materialised

    def mark_materialised(self, template_id: str, date: str) -> None:
        self._materialised.add((template_id, date))

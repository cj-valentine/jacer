from abc import ABC, abstractmethod

from jacer.models import DailyLog, Task, Template, TemplateItem


class Repository(ABC):
    """Storage interface for Jacer.

    Every concrete adapter (markdown, in-memory, future Iceberg) implements
    this contract. Routers and services depend on Repository, never on a
    specific adapter — this is the seam that keeps storage swappable.
    """

    # Tasks

    @abstractmethod
    def list_tasks(
        self,
        status: str | None = None,
        date: str | None = None,
    ) -> list[Task]: ...

    @abstractmethod
    def get_task(self, task_id: str) -> Task | None: ...

    @abstractmethod
    def save_task(self, task: Task) -> Task: ...

    @abstractmethod
    def delete_task(self, task_id: str) -> bool: ...

    # Templates

    @abstractmethod
    def list_templates(self) -> list[Template]: ...

    @abstractmethod
    def get_template(self, template_id: str) -> Template | None: ...

    @abstractmethod
    def save_template(self, template: Template) -> Template: ...

    @abstractmethod
    def delete_template(self, template_id: str) -> bool: ...

    # Template items

    @abstractmethod
    def list_template_items(self, template_id: str) -> list[TemplateItem]: ...

    @abstractmethod
    def get_template_item(self, item_id: str) -> TemplateItem | None: ...

    @abstractmethod
    def save_template_item(self, item: TemplateItem) -> TemplateItem: ...

    @abstractmethod
    def delete_template_item(self, item_id: str) -> bool: ...

    # Daily logs

    @abstractmethod
    def get_daily_log(self, log_date: str) -> DailyLog | None: ...

    @abstractmethod
    def save_daily_log(self, log: DailyLog) -> DailyLog: ...

    # Materialisation tracking

    @abstractmethod
    def is_materialised(self, template_id: str, date: str) -> bool: ...

    @abstractmethod
    def mark_materialised(self, template_id: str, date: str) -> None: ...

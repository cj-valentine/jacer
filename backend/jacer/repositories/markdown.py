import json
from datetime import datetime
from pathlib import Path
from typing import Any

import frontmatter

from jacer.models import Category, DailyLog, Task, Template, TemplateItem
from jacer.repositories.base import Repository


def _atomic_write(path: Path, content: str) -> None:
    """Write to a temp file then rename. Survives interrupted writes."""
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(path)


def _serialise_metadata(dump: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in dump.items():
        out[k] = v.isoformat() if isinstance(v, datetime) else v
    return out


def _dumps_post(metadata: dict[str, Any], body: str) -> str:
    post = frontmatter.Post(body, **metadata)
    return frontmatter.dumps(post)


class MarkdownRepository(Repository):
    """Markdown-on-disk adapter.

    Layout (relative to data_dir):
        tasks/<uuid>.md            Task records (description in body, rest in frontmatter)
        templates/<uuid>.md        Template records (frontmatter only)
        template-items/<uuid>.md   TemplateItem records (description in body)
        categories/<uuid>.md       Category records (frontmatter only)
        logs/<YYYY-MM-DD>.md       Daily log records (content in body)
        _materialised.json         Materialisation tracking index

    Writes are atomic (temp-file + rename). Malformed files are skipped on
    list operations rather than crashing the whole call.
    """

    def __init__(self, data_dir: Path | str) -> None:
        self.data_dir = Path(data_dir)
        self.tasks_dir = self.data_dir / "tasks"
        self.templates_dir = self.data_dir / "templates"
        self.template_items_dir = self.data_dir / "template-items"
        self.categories_dir = self.data_dir / "categories"
        self.logs_dir = self.data_dir / "logs"
        self.materialised_path = self.data_dir / "_materialised.json"

        for d in (
            self.tasks_dir,
            self.templates_dir,
            self.template_items_dir,
            self.categories_dir,
            self.logs_dir,
        ):
            d.mkdir(parents=True, exist_ok=True)

    # Tasks

    def list_tasks(self, status: str | None = None, date: str | None = None) -> list[Task]:
        tasks: list[Task] = []
        for path in sorted(self.tasks_dir.glob("*.md")):
            task = self._load_task(path)
            if task is not None:
                tasks.append(task)
        if status is not None:
            tasks = [t for t in tasks if t.status == status]
        if date is not None:
            tasks = [t for t in tasks if t.scheduled_date == date or t.instance_date == date]
        return tasks

    def get_task(self, task_id: str) -> Task | None:
        return self._load_task(self.tasks_dir / f"{task_id}.md")

    def save_task(self, task: Task) -> Task:
        dump = task.model_dump()
        body = dump.pop("description", "") or ""
        metadata = _serialise_metadata(dump)
        _atomic_write(self.tasks_dir / f"{task.id}.md", _dumps_post(metadata, body))
        return task

    def delete_task(self, task_id: str) -> bool:
        path = self.tasks_dir / f"{task_id}.md"
        if path.exists():
            path.unlink()
            return True
        return False

    def _load_task(self, path: Path) -> Task | None:
        data = self._read_post(path)
        if data is None:
            return None
        body = data.pop("__body", "") or ""
        if "description" not in data or not data["description"]:
            data["description"] = body
        try:
            return Task.model_validate(data)
        except Exception:
            return None

    # Templates

    def list_templates(self) -> list[Template]:
        templates: list[Template] = []
        for path in sorted(self.templates_dir.glob("*.md")):
            template = self._load_template(path)
            if template is not None:
                templates.append(template)
        return templates

    def get_template(self, template_id: str) -> Template | None:
        return self._load_template(self.templates_dir / f"{template_id}.md")

    def save_template(self, template: Template) -> Template:
        dump = template.model_dump()
        metadata = _serialise_metadata(dump)
        _atomic_write(self.templates_dir / f"{template.id}.md", _dumps_post(metadata, ""))
        return template

    def delete_template(self, template_id: str) -> bool:
        path = self.templates_dir / f"{template_id}.md"
        if path.exists():
            path.unlink()
            return True
        return False

    def _load_template(self, path: Path) -> Template | None:
        data = self._read_post(path)
        if data is None:
            return None
        data.pop("__body", None)
        try:
            return Template.model_validate(data)
        except Exception:
            return None

    # Template items

    def list_template_items(self, template_id: str) -> list[TemplateItem]:
        items: list[TemplateItem] = []
        for path in sorted(self.template_items_dir.glob("*.md")):
            item = self._load_template_item(path)
            if item is not None and item.template_id == template_id:
                items.append(item)
        return items

    def get_template_item(self, item_id: str) -> TemplateItem | None:
        return self._load_template_item(self.template_items_dir / f"{item_id}.md")

    def save_template_item(self, item: TemplateItem) -> TemplateItem:
        dump = item.model_dump()
        body = dump.pop("description", "") or ""
        metadata = _serialise_metadata(dump)
        _atomic_write(self.template_items_dir / f"{item.id}.md", _dumps_post(metadata, body))
        return item

    def delete_template_item(self, item_id: str) -> bool:
        path = self.template_items_dir / f"{item_id}.md"
        if path.exists():
            path.unlink()
            return True
        return False

    def _load_template_item(self, path: Path) -> TemplateItem | None:
        data = self._read_post(path)
        if data is None:
            return None
        body = data.pop("__body", "") or ""
        if "description" not in data or not data["description"]:
            data["description"] = body
        try:
            return TemplateItem.model_validate(data)
        except Exception:
            return None

    # Categories

    def list_categories(self) -> list[Category]:
        categories: list[Category] = []
        for path in sorted(self.categories_dir.glob("*.md")):
            category = self._load_category(path)
            if category is not None:
                categories.append(category)
        return categories

    def get_category(self, category_id: str) -> Category | None:
        return self._load_category(self.categories_dir / f"{category_id}.md")

    def save_category(self, category: Category) -> Category:
        metadata = _serialise_metadata(category.model_dump())
        _atomic_write(self.categories_dir / f"{category.id}.md", _dumps_post(metadata, ""))
        return category

    def delete_category(self, category_id: str) -> bool:
        path = self.categories_dir / f"{category_id}.md"
        if path.exists():
            path.unlink()
            return True
        return False

    def _load_category(self, path: Path) -> Category | None:
        data = self._read_post(path)
        if data is None:
            return None
        data.pop("__body", None)
        try:
            return Category.model_validate(data)
        except Exception:
            return None

    # Daily logs

    def get_daily_log(self, log_date: str) -> DailyLog | None:
        data = self._read_post(self.logs_dir / f"{log_date}.md")
        if data is None:
            return None
        body = data.pop("__body", "") or ""
        if "content" not in data or not data["content"]:
            data["content"] = body
        try:
            return DailyLog.model_validate(data)
        except Exception:
            return None

    def save_daily_log(self, log: DailyLog) -> DailyLog:
        dump = log.model_dump()
        body = dump.pop("content", "") or ""
        metadata = _serialise_metadata(dump)
        _atomic_write(self.logs_dir / f"{log.date}.md", _dumps_post(metadata, body))
        return log

    # Materialisation tracking

    def is_materialised(self, template_id: str, date: str) -> bool:
        index = self._load_materialised_index()
        return date in index.get(template_id, [])

    def mark_materialised(self, template_id: str, date: str) -> None:
        index = self._load_materialised_index()
        dates = index.setdefault(template_id, [])
        if date not in dates:
            dates.append(date)
            dates.sort()
            self._save_materialised_index(index)

    def _load_materialised_index(self) -> dict[str, list[str]]:
        if not self.materialised_path.exists():
            return {}
        try:
            return json.loads(self.materialised_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}

    def _save_materialised_index(self, index: dict[str, list[str]]) -> None:
        _atomic_write(
            self.materialised_path,
            json.dumps(index, indent=2, sort_keys=True),
        )

    # Internal helpers

    def _read_post(self, path: Path) -> dict[str, Any] | None:
        if not path.exists():
            return None
        try:
            with path.open("r", encoding="utf-8") as f:
                post = frontmatter.load(f)
        except Exception:
            return None
        data: dict[str, Any] = dict(post.metadata)
        data["__body"] = post.content
        return data

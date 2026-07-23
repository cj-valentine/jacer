from datetime import UTC, datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException

from jacer.deps import get_repository
from jacer.models import Task
from jacer.repositories.base import Repository
from jacer.schemas import DeleteResponse, TaskCreate, TaskUpdate

router = APIRouter()


@router.get("/", response_model=list[Task])
def list_tasks(
    status: str | None = None,
    date: str | None = None,
    repo: Repository = Depends(get_repository),
):
    return repo.list_tasks(status=status, date=date)


@router.post("/", response_model=Task, status_code=201)
def create_task(payload: TaskCreate, repo: Repository = Depends(get_repository)):
    now = datetime.now(UTC)
    task = Task(
        id=str(uuid4()),
        created_at=now,
        updated_at=now,
        **payload.model_dump(),
    )
    # ADR-004: status is canonical; is_completed is derived from it.
    task.is_completed = task.status == "done"
    return repo.save_task(task)


@router.get("/{task_id}", response_model=Task)
def get_task(task_id: str, repo: Repository = Depends(get_repository)):
    task = repo.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}", response_model=Task)
def update_task(
    task_id: str,
    payload: TaskUpdate,
    repo: Repository = Depends(get_repository),
):
    existing = repo.get_task(task_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Task not found")

    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        return existing

    for k, v in updates.items():
        setattr(existing, k, v)

    # ADR-004: status and is_completed are two views of one truth. Reconcile
    # them so callers can drive either field. status is canonical.
    #   - status supplied (with or without is_completed): status wins.
    #   - only is_completed supplied: it drives status
    #       (True -> "done", False -> "backlog").
    # Then is_completed is always re-derived from the resulting status, so the
    # pair can never be left inconsistent.
    if "status" not in updates and "is_completed" in updates:
        existing.status = "done" if updates["is_completed"] else "backlog"
    existing.is_completed = existing.status == "done"

    if existing.template_origin_id:
        existing.diverged = True

    existing.updated_at = datetime.now(UTC)
    return repo.save_task(existing)


@router.post("/{task_id}/reset-to-template", response_model=Task)
def reset_to_template(task_id: str, repo: Repository = Depends(get_repository)):
    """Restore a task's DEFINITION from its originating template item.

    Additive endpoint (ADR-006): a reset cannot be done client-side because any
    PATCH to a template-origin task re-sets diverged=True. This restores the
    definition fields — title, duration_minutes, category, scheduled_time — from
    the template item and clears diverged. It deliberately does NOT touch status,
    is_completed, scheduled_date or instance_date: reset is about definition, not
    placement or completion.
    """
    task = repo.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.template_origin_id is None:
        raise HTTPException(
            status_code=409,
            detail="Task is not derived from a template",
        )

    item = repo.get_template_item(task.template_origin_id)
    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Originating template item no longer exists",
        )

    task.title = item.title
    task.duration_minutes = item.duration_minutes
    task.category_id = item.category_id
    task.scheduled_time = item.default_time
    task.diverged = False
    task.updated_at = datetime.now(UTC)
    return repo.save_task(task)


@router.delete("/{task_id}", response_model=DeleteResponse)
def delete_task(task_id: str, repo: Repository = Depends(get_repository)):
    if not repo.delete_task(task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    return DeleteResponse()

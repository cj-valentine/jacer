from datetime import UTC, datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException

from jacer.deps import get_repository
from jacer.models import Template
from jacer.repositories.base import Repository
from jacer.schemas import DeleteResponse, LockResponse, TemplateCreate, TemplateUpdate

router = APIRouter()


@router.get("/", response_model=list[Template])
def list_templates(repo: Repository = Depends(get_repository)):
    return repo.list_templates()


@router.post("/", response_model=Template, status_code=201)
def create_template(payload: TemplateCreate, repo: Repository = Depends(get_repository)):
    if payload.cadence == "fortnightly" and payload.week_a_start_date is None:
        raise HTTPException(
            status_code=422,
            detail="week_a_start_date is required for fortnightly templates",
        )
    now = datetime.now(UTC)
    template = Template(
        id=str(uuid4()),
        is_locked=False,
        created_at=now,
        updated_at=now,
        **payload.model_dump(),
    )
    return repo.save_template(template)


@router.get("/{template_id}", response_model=Template)
def get_template(template_id: str, repo: Repository = Depends(get_repository)):
    template = repo.get_template(template_id)
    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.patch("/{template_id}", response_model=Template)
def update_template(
    template_id: str,
    payload: TemplateUpdate,
    repo: Repository = Depends(get_repository),
):
    existing = repo.get_template(template_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Template not found")

    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        return existing

    for k, v in updates.items():
        setattr(existing, k, v)

    if existing.cadence == "fortnightly" and existing.week_a_start_date is None:
        raise HTTPException(
            status_code=422,
            detail="week_a_start_date is required for fortnightly templates",
        )

    existing.updated_at = datetime.now(UTC)
    return repo.save_template(existing)


@router.delete("/{template_id}", response_model=DeleteResponse)
def delete_template(template_id: str, repo: Repository = Depends(get_repository)):
    if not repo.delete_template(template_id):
        raise HTTPException(status_code=404, detail="Template not found")
    return DeleteResponse()


@router.post("/{template_id}/lock", response_model=LockResponse)
def lock_template(template_id: str, repo: Repository = Depends(get_repository)):
    template = repo.get_template(template_id)
    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    template.is_locked = True
    template.updated_at = datetime.now(UTC)
    repo.save_template(template)
    return LockResponse(template_id=template_id, is_locked=True)


@router.post("/{template_id}/unlock", response_model=LockResponse)
def unlock_template(template_id: str, repo: Repository = Depends(get_repository)):
    template = repo.get_template(template_id)
    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    template.is_locked = False
    template.updated_at = datetime.now(UTC)
    repo.save_template(template)
    return LockResponse(template_id=template_id, is_locked=False)

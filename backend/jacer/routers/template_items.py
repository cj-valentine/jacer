from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException

from jacer.deps import get_repository
from jacer.models import TemplateItem
from jacer.repositories.base import Repository
from jacer.schemas import DeleteResponse, TemplateItemCreate, TemplateItemUpdate

router = APIRouter()


@router.get("/templates/{template_id}/items", response_model=list[TemplateItem])
def list_items(template_id: str, repo: Repository = Depends(get_repository)):
    if repo.get_template(template_id) is None:
        raise HTTPException(status_code=404, detail="Template not found")
    return repo.list_template_items(template_id)


@router.post(
    "/templates/{template_id}/items",
    response_model=TemplateItem,
    status_code=201,
)
def create_item(
    template_id: str,
    payload: TemplateItemCreate,
    repo: Repository = Depends(get_repository),
):
    template = repo.get_template(template_id)
    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    if template.cadence == "weekly" and payload.week_slot is not None:
        raise HTTPException(
            status_code=422,
            detail="week_slot is only valid on fortnightly templates",
        )
    item = TemplateItem(
        id=str(uuid4()),
        template_id=template_id,
        **payload.model_dump(),
    )
    return repo.save_template_item(item)


@router.get("/template-items/{item_id}", response_model=TemplateItem)
def get_item(item_id: str, repo: Repository = Depends(get_repository)):
    item = repo.get_template_item(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Template item not found")
    return item


@router.patch("/template-items/{item_id}", response_model=TemplateItem)
def update_item(
    item_id: str,
    payload: TemplateItemUpdate,
    repo: Repository = Depends(get_repository),
):
    existing = repo.get_template_item(item_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Template item not found")

    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        return existing

    for k, v in updates.items():
        setattr(existing, k, v)
    return repo.save_template_item(existing)


@router.delete("/template-items/{item_id}", response_model=DeleteResponse)
def delete_item(item_id: str, repo: Repository = Depends(get_repository)):
    if not repo.delete_template_item(item_id):
        raise HTTPException(status_code=404, detail="Template item not found")
    return DeleteResponse()

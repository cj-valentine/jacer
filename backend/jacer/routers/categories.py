from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException

from jacer.deps import get_repository
from jacer.models import CATEGORY_PALETTE, Category
from jacer.repositories.base import Repository
from jacer.schemas import CategoryCreate, CategoryUpdate, DeleteResponse

router = APIRouter()


def _next_palette_colour(repo: Repository) -> str:
    """Round-robin the next palette colour, so fresh categories get distinct
    muted tones without the caller having to choose."""
    return CATEGORY_PALETTE[len(repo.list_categories()) % len(CATEGORY_PALETTE)]


def _validate_colour(colour: str | None) -> None:
    if colour is not None and colour not in CATEGORY_PALETTE:
        raise HTTPException(
            status_code=422,
            detail=f"colour must be one of the preset palette: {CATEGORY_PALETTE}",
        )


# Specific route before the generic /{category_id} routes, so "palette" is not
# matched as an id.
@router.get("/palette", response_model=list[str])
def get_palette():
    """The fixed muted palette category colours are drawn from — a single source
    of truth the frontend renders its swatch picker from."""
    return CATEGORY_PALETTE


@router.get("/", response_model=list[Category])
def list_categories(repo: Repository = Depends(get_repository)):
    return repo.list_categories()


@router.post("/", response_model=Category, status_code=201)
def create_category(payload: CategoryCreate, repo: Repository = Depends(get_repository)):
    _validate_colour(payload.colour)
    category = Category(
        id=str(uuid4()),
        name=payload.name,
        colour=payload.colour or _next_palette_colour(repo),
    )
    return repo.save_category(category)


@router.get("/{category_id}", response_model=Category)
def get_category(category_id: str, repo: Repository = Depends(get_repository)):
    category = repo.get_category(category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.patch("/{category_id}", response_model=Category)
def update_category(
    category_id: str,
    payload: CategoryUpdate,
    repo: Repository = Depends(get_repository),
):
    existing = repo.get_category(category_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Category not found")

    updates = payload.model_dump(exclude_unset=True)
    _validate_colour(updates.get("colour"))
    for k, v in updates.items():
        setattr(existing, k, v)
    return repo.save_category(existing)


@router.delete("/{category_id}", response_model=DeleteResponse)
def delete_category(category_id: str, repo: Repository = Depends(get_repository)):
    if repo.get_category(category_id) is None:
        raise HTTPException(status_code=404, detail="Category not found")

    # Clear dangling references so nothing points at a category that no longer
    # exists (Phase 3.5, Amendment 2 — "clear on delete"). Tasks and template
    # items referencing this category fall back to uncategorised.
    for task in repo.list_tasks():
        if task.category_id == category_id:
            task.category_id = None
            repo.save_task(task)
    for template in repo.list_templates():
        for item in repo.list_template_items(template.id):
            if item.category_id == category_id:
                item.category_id = None
                repo.save_template_item(item)

    repo.delete_category(category_id)
    return DeleteResponse()

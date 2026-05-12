from datetime import date as date_type, datetime

from fastapi import APIRouter, Depends, HTTPException

from jacer.deps import get_repository
from jacer.models import Task
from jacer.repositories.base import Repository
from jacer.schemas import HorizonMaterialiseResponse, MaterialiseResponse
from jacer.services.materialise import materialise_day, materialise_horizon

router = APIRouter()


def _validate_date(value: str) -> None:
    try:
        date_type.fromisoformat(value)
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=f"date must be YYYY-MM-DD, got {value!r}",
        ) from exc


@router.get("/{date}", response_model=list[Task])
def list_day_tasks(date: str, repo: Repository = Depends(get_repository)):
    _validate_date(date)
    return repo.list_tasks(date=date)


@router.post("/{date}/materialise", response_model=MaterialiseResponse)
def materialise(date: str, repo: Repository = Depends(get_repository)):
    _validate_date(date)
    created = materialise_day(repo, date)
    return MaterialiseResponse(
        date=date,
        created_count=len(created),
        created_task_ids=[t.id for t in created],
    )


@router.post("/horizon/materialise", response_model=HorizonMaterialiseResponse)
def materialise_horizon_endpoint(
    days: int = 14,
    start: str | None = None,
    repo: Repository = Depends(get_repository),
):
    if days < 1 or days > 60:
        raise HTTPException(status_code=422, detail="days must be between 1 and 60")
    if start is None:
        start = datetime.now().date().isoformat()
    else:
        _validate_date(start)

    created = materialise_horizon(repo, start, days)
    return HorizonMaterialiseResponse(
        start_date=start,
        days=days,
        created_count=len(created),
        created_task_ids=[t.id for t in created],
    )

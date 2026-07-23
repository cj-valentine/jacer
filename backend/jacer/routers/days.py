import datetime as dt

from fastapi import APIRouter, Depends, HTTPException

from jacer.deps import get_repository
from jacer.models import Task
from jacer.repositories.base import Repository
from jacer.schemas import HorizonMaterialiseResponse, MaterialiseResponse
from jacer.services.materialise import (
    materialise_day,
    materialise_horizon,
    sweep_stale_days,
)

router = APIRouter()


def _validate_date(value: str) -> None:
    try:
        dt.date.fromisoformat(value)
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=f"date must be YYYY-MM-DD, got {value!r}",
        ) from exc


# Specific routes must be declared before the generic /{date} routes,
# otherwise FastAPI would match 'horizon' as a date and validation would
# reject it before reaching this handler.
@router.post("/horizon/materialise", response_model=HorizonMaterialiseResponse)
def materialise_horizon_endpoint(
    days: int = 14,
    start: str | None = None,
    repo: Repository = Depends(get_repository),
):
    if days < 1 or days > 60:
        raise HTTPException(status_code=422, detail="days must be between 1 and 60")
    if start is None:
        start = dt.datetime.now().date().isoformat()
    else:
        _validate_date(start)

    created = materialise_horizon(repo, start, days)

    # Roll any now-past template tasks into their day's log and off the board.
    # The board fires this endpoint on load, so the sweep runs as part of the
    # normal materialisation cycle (ADR-005) — no separate endpoint needed. The
    # boundary is the real "today", independent of the horizon start.
    sweep_stale_days(repo, dt.date.today())

    return HorizonMaterialiseResponse(
        start_date=start,
        days=days,
        created_count=len(created),
        created_task_ids=[t.id for t in created],
    )


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

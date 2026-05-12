from fastapi import APIRouter

from jacer import __version__

router = APIRouter()


@router.get("/")
def root() -> dict[str, str]:
    return {"app": "jacer", "version": __version__, "status": "ok"}


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

import os
from pathlib import Path

from jacer.repositories.base import Repository
from jacer.repositories.markdown import MarkdownRepository
from jacer.repositories.memory import InMemoryRepository

_repository: Repository | None = None


def get_repository() -> Repository:
    """Resolve the active Repository adapter.

    Selected via the `JACER_REPOSITORY` env var:

      - `markdown` (default) — persists to disk as markdown files. Data
        directory is `JACER_DATA_DIR` (default `./data`).
      - `memory` — ephemeral, in-process. Used in tests and dev-only.
    """
    global _repository
    if _repository is None:
        kind = os.environ.get("JACER_REPOSITORY", "markdown")
        if kind == "memory":
            _repository = InMemoryRepository()
        elif kind == "markdown":
            data_dir = Path(os.environ.get("JACER_DATA_DIR", "./data"))
            _repository = MarkdownRepository(data_dir)
        else:
            raise ValueError(f"Unknown JACER_REPOSITORY: {kind!r}")
    return _repository


def reset_repository() -> None:
    """Reset the cached repository. Useful in tests."""
    global _repository
    _repository = None

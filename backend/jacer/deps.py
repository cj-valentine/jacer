from jacer.repositories.base import Repository
from jacer.repositories.memory import InMemoryRepository

_repository: Repository | None = None


def get_repository() -> Repository:
    """Resolve the active Repository adapter.

    Chunk 1 returns an InMemoryRepository unconditionally. Chunk 2 swaps in
    the MarkdownRepository as the default and selects via env var.
    """
    global _repository
    if _repository is None:
        _repository = InMemoryRepository()
    return _repository

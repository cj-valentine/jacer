import pytest
from fastapi.testclient import TestClient

from jacer.deps import get_repository
from jacer.main import app
from jacer.repositories.markdown import MarkdownRepository
from jacer.repositories.memory import InMemoryRepository


@pytest.fixture(params=["memory", "markdown"])
def repository(request, tmp_path):
    """Parametrised — every contract test runs against both adapters."""
    if request.param == "memory":
        return InMemoryRepository()
    return MarkdownRepository(tmp_path / "data")


@pytest.fixture
def memory_repository():
    """Non-parametrised, for route tests that don't care about persistence."""
    return InMemoryRepository()


@pytest.fixture
def client(memory_repository):
    app.dependency_overrides[get_repository] = lambda: memory_repository
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def both_repos_client(repository):
    """Like `client`, but parametrised over both adapters (see `repository`).

    Used where router behaviour must be proven to round-trip through real
    persistence — e.g. the ADR-004 status/is_completed reconciliation, whose
    derived field the markdown adapter has to serialise and reload correctly.
    """
    app.dependency_overrides[get_repository] = lambda: repository
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()

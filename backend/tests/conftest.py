import pytest
from fastapi.testclient import TestClient

from jacer.deps import get_repository
from jacer.main import app
from jacer.repositories.memory import InMemoryRepository


@pytest.fixture
def repository() -> InMemoryRepository:
    return InMemoryRepository()


@pytest.fixture
def client(repository: InMemoryRepository):
    app.dependency_overrides[get_repository] = lambda: repository
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()

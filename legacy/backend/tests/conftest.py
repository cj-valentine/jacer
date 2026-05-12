import os
import shutil
import pytest
from fastapi.testclient import TestClient
from backend.main import app
import backend.services.file_io as file_io

@pytest.fixture(scope="session", autouse=True)
def test_data_dir():
    """Create a temporary data directory for testing."""
    test_base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    test_data_dir = os.path.join(test_base_dir, "test_data")
    
    # Override the directory paths in file_io
    file_io.DATA_DIR = test_data_dir
    file_io.TASKS_DIR = os.path.join(test_data_dir, "tasks")
    file_io.LOGS_DIR = os.path.join(test_data_dir, "logs")
    file_io.TEMPLATES_DIR = os.path.join(test_data_dir, "templates")
    file_io.ARCHIVE_DIR = os.path.join(test_data_dir, "archive")
    
    # Create directories
    for d in [file_io.TASKS_DIR, file_io.LOGS_DIR, file_io.TEMPLATES_DIR, file_io.ARCHIVE_DIR]:
        os.makedirs(d, exist_ok=True)
        
    yield test_data_dir
    
    # Cleanup after all tests run
    if os.path.exists(test_data_dir):
        shutil.rmtree(test_data_dir)

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture(autouse=True)
def clear_tasks_between_tests():
    """Clear all markdown files between each test to prevent state bleeding."""
    # We yield first so the test runs, then cleanup happens after
    yield
    for directory in [file_io.TASKS_DIR, file_io.LOGS_DIR, file_io.TEMPLATES_DIR, file_io.ARCHIVE_DIR]:
        for file in os.listdir(directory):
            filepath = os.path.join(directory, file)
            if os.path.isfile(filepath):
                os.unlink(filepath)

# tests/conftest.py
import sys
import os
import pytest

# Add the project root directory to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

@pytest.fixture(scope="session")
def db_dsn():
    """Provide a reusable database DSN for tests if needed."""
    from src.config import get_db_dsn
    return get_db_dsn()

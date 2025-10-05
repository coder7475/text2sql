import pytest
import tempfile
import os

@pytest.fixture
def temp_dir():
    td = tempfile.TemporaryDirectory()
    yield td.name
    td.cleanup()

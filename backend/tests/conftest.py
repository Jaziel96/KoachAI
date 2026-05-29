import os
import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("WHATSAPP_VERIFY_TOKEN", "test_token")

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)

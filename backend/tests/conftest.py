import os
import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("WHATSAPP_VERIFY_TOKEN", "test_token")
os.environ.setdefault("WHATSAPP_PHONE_NUMBER_ID", "test_phone_id")

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)

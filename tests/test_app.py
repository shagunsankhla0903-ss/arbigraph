import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def test_root_returns_message():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "ArbiGraph API is running."}


def test_cycles_requires_api_key():
    response = client.get("/v1/cycles")
    assert response.status_code == 401


def test_cycles_with_valid_key():
    response = client.get("/v1/cycles", headers={"X-API-Key": "test-key-123"})
    assert response.status_code == 200
    assert "cycles" in response.json()
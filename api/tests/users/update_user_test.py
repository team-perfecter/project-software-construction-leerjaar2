from unittest.mock import patch
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_update_profile(client):
    fake_user = {
        "username": "waddapjes",
    }

    response = client.post("/update_profile", json=fake_user)
    assert response.status_code == 201

def test_update_profile_without_user_changes(client):
    fake_user = {}

    response = client.post("/update_profile", json=fake_user)
    assert response.status_code == 400
from unittest.mock import patch
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_update_profile(client_with_token):
    client, headers = client_with_token("user")
    fake_user = {
        "username": "waddapjes",
    }
    response = client.put("/update_profile", json=fake_user, headers=headers)
    assert response.status_code == 201
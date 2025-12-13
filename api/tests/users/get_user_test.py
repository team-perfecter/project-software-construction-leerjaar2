from unittest.mock import patch
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_get_all_users(client):
    response = client.get("/users")
    assert response.status_code == 200

def test_get_user_as_user(client_with_token):
    client, headers = client_with_token("user")
    response = client.get("/admin/users/1", headers=headers)
    assert response.status_code == 404

def test_get_user_as_user(client_with_token):
    client, headers = client_with_token("admin")
    response = client.get("/admin/users/1", headers=headers)
    assert response.status_code == 200
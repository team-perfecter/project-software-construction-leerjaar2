from unittest.mock import patch
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_delete_user_as_admin(client_with_token):
    client, headers = client_with_token("superadmin")
    response = client.delete("/users/5", headers=headers)
    assert response.status_code == 200

def test_delete_user_doesnt_exist(client_with_token):
    client, headers = client_with_token("superadmin")
    response = client.delete("/users/9999999", headers=headers)
    assert response.status_code == 404

def test_delete_user_as_user(client_with_token):
    client, headers = client_with_token("user")
    response = client.delete("/users/1", headers=headers)
    assert response.status_code == 403


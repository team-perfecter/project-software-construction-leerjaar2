from unittest.mock import patch
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_delete_user(client_with_token):
    client, headers = client_with_token("superadmin")
    response = client.delete("/admin/users/6", headers=headers)
    assert response.status_code == 200

def test_delete_user_that_doesnt_exist(client_with_token):
    client, headers = client_with_token("superadmin")
    response = client.delete("/admin/users/99999", headers=headers)
    assert response.status_code == 404
from unittest.mock import patch
from fastapi.testclient import TestClient
from api.main import app
from api.tests.conftest import get_last_uid

client = TestClient(app)

def test_delete_user(client_with_token):
    user_id = get_last_uid(client_with_token)
    client, headers = client_with_token("superadmin")
    response = client.delete(f"/users/{user_id}", headers=headers)
    assert response.status_code == 200

def test_delete_user_that_doesnt_exist(client_with_token):
    client, headers = client_with_token("superadmin")
    response = client.delete("/users/99999", headers=headers)
    assert response.status_code == 404
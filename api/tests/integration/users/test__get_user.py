from unittest.mock import patch
from fastapi.testclient import TestClient
from api.main import app
from api.tests.conftest import get_last_uid

client = TestClient(app)

def test_get_all_users_as_admin(client_with_token):
    client, headers = client_with_token("lotadmin")
    response = client.get("/users", headers=headers)
    assert response.status_code == 200

def test_get_all_users_as_superadmin(client_with_token):
    client, headers = client_with_token("superadmin")
    response = client.get("/users", headers=headers)
    assert response.status_code == 200


def test_get_user_as_superadmin(client_with_token):
    user_id = get_last_uid(client_with_token)
    client, headers = client_with_token("superadmin")
    response = client.get(f"/get_user/{user_id}", headers=headers)
    assert response.status_code == 200


def test_get_user_as_user(client_with_token):
    user_id = get_last_uid(client_with_token)
    client, headers = client_with_token("user")
    response = client.get(f"/get_user/{user_id}", headers=headers)
    assert response.status_code == 403


def test_get_user_not_logged_in(client):
    response = client.get("/get_user/1")
    assert response.status_code == 401


def test_get_user_doesnt_exist(client_with_token):
    client, headers = client_with_token("superadmin")
    response = client.get("/get_user/99999", headers=headers)
    assert response.status_code == 404


def test_profile_when_loggedin(client_with_token):
    client, headers = client_with_token("user")
    response = client.get("/profile", headers=headers)
    assert response.status_code == 200


def test_get_profile_when_not_loggedin(client):
    response = client.get("/profile")
    assert response.status_code == 401


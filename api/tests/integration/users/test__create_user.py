from unittest.mock import patch
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_register_not_all_field_filled(client):
    fake_user = {
        "password": "Waddap",
        "name": "waddap",
        "email": "waddap@gmail.com",
        "phone": "1234567890",
        "birth_year": "2003",
    }
    response = client.post("/register", json=fake_user)
    assert response.status_code == 422


def test_register(client):
    fake_user = {
        "username": "Waddap_User",
        "password": "Waddap",
        "name": "waddap",
        "email": "waddap@gmail.com",
        "phone": "1234567890",
        "birth_year": "2003",
    }
    response = client.post("/register", json=fake_user)
    assert response.status_code == 201


def test_register_same_name(client):
    fake_user = {
        "username": "superadmin",
        "password": "Waddap",
        "name": "waddap",
        "email": "waddap@gmail.com",
        "phone": "1234567890",
        "birth_year": "2003",
    }
    response = client.post("/register", json=fake_user)
    assert response.status_code == 409


def test_create_user(client_with_token):
    client, headers = client_with_token("superadmin")
    fake_user = {
        "username": "Waddap_user",
        "password": "Waddap_user",
        "name": "user",
        "email": "user@gmail.com",
        "phone": "1234567890",
        "birth_year": "2003",
        "role": "user"
    }
    response = client.post("/create_user", json=fake_user, headers=headers)
    assert response.status_code == 201


def test_create_admin_already_exists(client_with_token):
    client, headers = client_with_token("superadmin")
    fake_user = {
        "username": "Waddap_user",
        "password": "Waddap_user",
        "name": "user",
        "email": "user@gmail.com",
        "phone": "1234567890",
        "birth_year": "2003",
        "role": "user"
    }
    response = client.post("/create_user", json=fake_user, headers=headers)
    assert response.status_code == 409


def test_login(client): 
    fake_user = {
        "username": "superadmin",
        "password": "admin123",
    }
    response = client.post("/login", json=fake_user)
    assert response.status_code == 200


def test_login_wrong_password(client):
    fake_user = {
        "username": "superadmin",
        "password": "wrong",
    }
    response = client.post("/login", json=fake_user)
    assert response.status_code == 401


def test_login_not_existing_username(client):
    fake_user = {
        "username": "wrong",
        "password": "wrong",
    }
    response = client.post("/login", json=fake_user)
    assert response.status_code == 404


def test_logout(client_with_token):
    client, headers = client_with_token("user")
    response = client.post("/logout", headers=headers)
    assert response.status_code == 200


def test_logout_without_a_login(client):
    response = client.post("/logout")
    assert response.status_code == 401

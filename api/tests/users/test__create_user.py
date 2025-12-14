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


def test_register_not_existing_password(client):
    fake_user = {
        "username": "Waddap_User",
        "password": "woow",
    }
    response = client.post("/login", json=fake_user)
    assert response.status_code == 401



def test_register_same_name(client):
    fake_user = {
        "username": "Waddap_User",
        "password": "Waddap",
        "name": "waddap",
        "email": "waddap@gmail.com",
        "phone": "1234567890",
        "birth_year": "2003",
    }
    response = client.post("/register", json=fake_user)
    assert response.status_code == 409


def test_create_admin(client_with_token):
    client, headers = client_with_token("superadmin")
    fake_user = {
        "username": "Waddap_admin",
        "password": "Waddap_admin",
        "name": "admin",
        "email": "adminnetje@gmail.com",
        "phone": "1234567890",
        "birth_year": "2003",
        "role": "admin"
    }
    response = client.post("/create_admin", json=fake_user, headers=headers)
    assert response.status_code == 201


def test_create_admin_already_exists(client_with_token):
    client, headers = client_with_token("superadmin")
    fake_user = {
        "username": "Waddap_admin",
        "password": "Waddap_admin",
        "name": "admin",
        "email": "adminnetje@gmail.com",
        "phone": "1234567890",
        "birth_year": "2003",
        "role": "admin"
    }
    response = client.post("/create_admin", json=fake_user, headers=headers)
    assert response.status_code == 409


def test_login(client): 
    fake_user = {
        "username": "Waddap_User",
        "password": "Waddap",
    }
    response = client.post("/login", json=fake_user)
    assert response.status_code == 200


def test_login_not_existing_username(client):
    fake_user = {
        "username": "user_waddap",
        "password": "Waddap",
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
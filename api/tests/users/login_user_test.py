from unittest.mock import patch
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_logout_without_a_login(client):
    response = client.post("/logout")
    assert response.status_code == 401

def test_get_profile_when_not_loggedin(client):
    response = client.get("/profile")
    assert response.status_code == 401

def test_login_not_existing_username(client):
    
    fake_user = {
        "username": "user_waddap",
        "password": "Waddap",
    }
    response = client.post("/login", json=fake_user)
    assert response.status_code == 404

def test_register_not_existing_password(client):
    
    fake_user = {
        "username": "Waddap_User",
        "password": "woow",
    }
    response = client.post("/login", json=fake_user)
    assert response.status_code == 401

def test_login(client):
        
    fake_user = {
        "username": "Waddap_User",
        "password": "Waddap",
    }
    response = client.post("/login", json=fake_user)
    assert response.status_code == 200

def test_profile_when_loggedin(client_with_token):
    client, headers = client_with_token("user")
    response = client.get("/profile", headers=headers)
    assert response.status_code == 200

def test_profile_when_not_loggedin(client):
    response = client.get("/profile")
    assert response.status_code == 401

def test_get_user(client):
    response = client.get("/get_user/1")
    assert response.status_code == 200

def test_get_user_doesnt_exist(client):
    response = client.get("/get_user/2000")
    assert response.status_code == 404

def test_logout(client_with_token):
    client, headers = client_with_token("user")
    response = client.post("/logout", headers=headers)
    assert response.status_code == 200
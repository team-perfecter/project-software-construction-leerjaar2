from unittest.mock import patch
from datetime import datetime, timedelta
import jwt
import pytest
from fastapi.testclient import TestClient

client = TestClient(app)

'''
A function that creates a new authorization token so a user can be verified
'''
def create_test_token(username: str):
    expire = datetime.utcnow() + timedelta(minutes=30)
    token = jwt.encode({"sub": username, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)
    return token

valid_token = create_test_token("alice")
valid_headers = {"Authorization": f"Bearer {valid_token}"}
invalid_headers = {"Authorization": "Bearer invalid"}

'''
Fake data
'''
def get_fake_user(username: str):
    users = {
        "alice": {
            "username": "alice",
            "email": "alice@example.com",
            "full_name": "Alice Doe",
            "role": "user"
        },
        "bob": {
            "username": "bob",
            "email": "bob@example.com",
            "full_name": "Bob Smith",
            "role": "admin"
        }
    }
    return users.get(username)

'''
Haal profielgegevens op.
'''
def test_get_profile_when_authorized():
    with patch("app.routers.profile.db_get_user", side_effect=get_fake_user):
        response = client.get("/profile", headers=valid_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "alice"
        assert "email" in data
        assert "full_name" in data
        assert "role" in data

'''
Kijken of gebruiker is ingelogd.
'''
def test_get_profile_not_authorized():
    response = client.get("/profile", headers=invalid_headers)
    assert response.status_code == 401

'''
Gebruiker probeert data van een ander op te halen.
'''
def test_get_other_user_profile_forbidden():
    with patch("app.routers.profile.db_get_user", side_effect=get_fake_user):
        response = client.get("/profile?username=bob", headers=valid_headers)
        assert response.status_code in [401, 403]

'''
Controleer of de profieldata compleet is.
'''
def test_get_profile_data_is_complete():
    with patch("app.routers.profile.db_get_user", side_effect=get_fake_user):
        response = client.get("/profile", headers=valid_headers)
        data = response.json()
        expected_keys = {"username", "email", "full_name", "role"}
        assert expected_keys.issubset(data.keys())

'''
Logout is de gebruiker ingelogd?
'''
def test_logout_when_logged_in():
    response = client.get("/logout", headers=valid_headers)
    assert response.status_code == 200
    msg = response.json().get("message", "").lower()
    assert "logout" in msg

'''
Logout zonder geldige token.
'''
def test_logout_when_not_logged_in():
    response = client.get("/logout", headers=invalid_headers)
    assert response.status_code == 401
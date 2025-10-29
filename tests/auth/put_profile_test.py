from unittest.mock import patch
from datetime import datetime, timedelta
import jwt
import pytest
from fastapi.testclient import TestClient
from ../../app import app

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
def fake_update_user(username: str, data: dict):
    if username != "alice":
        return {"error": "Forbidden"}
    if not data or "email" not in data:
        return {"error": "Incomplete data"}
    if "password" in data:
        return {"message": "Password updated successfully"}
    return {"message": "Profile updated successfully"}

'''
Als gebruiker niet ingelogd is en probeert aan te passen.
'''
def test_update_profile_not_authorized():
    payload = {"email": "newalice@example.com"}
    response = client.put("/profile", headers=invalid_headers, json=payload)
    assert response.status_code == 401

'''
Gebruiker probeert data van een andere user aan te passen.
'''
def test_update_other_user_profile_forbidden():
    with patch("app.routers.profile.db_update_user", side_effect=fake_update_user):
        payload = {"email": "bob@example.com"}
        response = client.put("/profile?username=bob", headers=valid_headers, json=payload)
        assert response.status_code in [401, 403]
        data = response.json()
        assert "error" in data

'''
Ingelogde gebruiker past eigen data succesvol aan.
'''
def test_update_own_profile_success():
    with patch("app.routers.profile.db_update_user", side_effect=fake_update_user):
        payload = {"email": "newalice@example.com"}
        response = client.put("/profile", headers=valid_headers, json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "Profile updated" in data["message"]

'''
Ingelogde gebruiker past eigen data aan met incomplete data.
'''
def test_update_own_profile_incomplete_data():
    with patch("app.routers.profile.db_update_user", side_effect=fake_update_user):
        payload = {}
        response = client.put("/profile", headers=valid_headers, json=payload)
        assert response.status_code in [400, 422]
        data = response.json()
        assert "error" in data

'''
Gebruiker probeert eigen wachtwoord te wijzigen.
'''
def test_update_own_password():
    with patch("app.routers.profile.db_update_user", side_effect=fake_update_user):
        payload = {"password": "newpassword123"}
        response = client.put("/profile", headers=valid_headers, json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "Password updated" in data["message"]
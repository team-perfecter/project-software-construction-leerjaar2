from unittest.mock import patch
from datetime import datetime, timedelta
import jwt
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from api.auth_utils import SECRET_KEY
from api.datatypes.user import UserCreate

with patch("psycopg2.connect"):
    from api.main import app

client = TestClient(app)

'''
A function that creates a new authorization token so a user can be verified
'''
def create_test_token(username: str):
    SECRET_KEY = "secret"
    ALGORITHM = "HS256"
    expire = datetime.utcnow() + timedelta(minutes=30)
    token = jwt.encode({"sub": username, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)
    return token

valid_token = create_test_token("alice")
valid_headers = {"Authorization": f"Bearer {valid_token}"}

'''
Fake data
'''
def fake_register_user(user: UserCreate):
    if user.username and user.password and user.email:
        return {"message": "User registered successfully"}
    else:
        return {"error": "Incomplete data"}

def fake_login_user(data):
    if data.get("username") == "alice" and data.get("password") == "secret123":
        return {"access_token": "fake_token", "token_type": "bearer"}
    elif data.get("username") == "alice":
        return {"error": "Incorrect password"}
    else:
        return {"error": "User not found"}

# The function this function mocks requires one input, so this function also gets one input even though it doesnt do anything
def fake_get_empty_user(username: str):
    return

'''
Gebruiker maakt een nieuw profiel aan.
'''
@patch("api.app.routers.profile.user_model.create_user", side_effect=fake_register_user)
@patch("api.app.routers.profile.user_model.get_user_by_username", side_effect=fake_get_empty_user)
def test_register_new_user(mock_create_user, mock_get_empty_user):
    payload = {
        "name": "new_user",
        "username": "new_user",
        "password": "test123",
        "email": "new_user@example.com"
    }
    response = client.post("/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "User created" in data["message"]

'''
Probeer een profiel aan te maken met incomplete data.
'''
@patch("api.app.routers.profile.user_model.create_user", side_effect=fake_register_user)
@patch("api.app.routers.profile.user_model.get_user_by_username", side_effect=fake_get_empty_user)
def test_register_user_incomplete_data(mock_create_user, mock_get_empty_user):
    payload = {"username": "missing_password"}
    response = client.post("/register", json=payload)
    assert response.status_code in [400, 422]
    data = response.json()
    assert "error" in data or "detail" in data

'''
Gebruiker gebruikt een verkeerd wachtwoord.
'''
def test_login_wrong_password():
    with patch("app.routers.auth.db_login_user", side_effect=fake_login_user):
        payload = {"username": "alice", "password": "wrongpass"}
        response = client.post("/login", json=payload)
        assert response.status_code in [401, 403]
        data = response.json()
        assert "error" in data
        assert "Incorrect password" in data["error"]

'''
Proberen in te loggen met een niet bestaand account.
'''
def test_login_nonexistent_user():
    with patch("app.routers.auth.db_login_user", side_effect=fake_login_user):
        payload = {"username": "unknown", "password": "test123"}
        response = client.post("/login", json=payload)
        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert "User not found" in data["error"]

'''
Succesvol inloggen.
'''
def test_login_success():
    with patch("app.routers.auth.db_login_user", side_effect=fake_login_user):
        payload = {"username": "alice", "password": "secret123"}
        response = client.post("/login", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
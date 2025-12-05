from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from unittest.mock import patch
import jwt
from api.datatypes.user import User

with patch("psycopg2.connect"):
    from api.main import app
    from api.auth_utils import SECRET_KEY, ALGORITHM, get_current_user


client = TestClient(app)
'''
A function that creates a new authorization token so a user can be verified
'''
def create_test_token(username: str):
    expire = datetime.utcnow() + timedelta(minutes=30)
    payload = {
        "sub": username,
        "exp": expire,
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

valid_token = create_test_token("alice")
valid_headers = {"Authorization": f"Bearer {valid_token}"}
invalid_headers = {"Authorization": "Bearer invalid"}

def fake_update_user(user_id, update_data):
    pass

def get_fake_user(username: str) -> User | None:
    users = [
        User(
            id=0,
            username="alice",
            password="password",
            email="alice@example.com",
            name="Alice Doe",
            phone="0612345678",
            birth_year=1995,
            created_at=datetime.now(),
            role="user",
        ),
        User(
            id=1,
            username="bob",
            password="password",
            email="bob@example.com",
            name="Bob Smith",
            phone="0698765432",
            created_at=datetime.now(),
            role="admin",
        )
    ]
    result: User | None = None
    for user in users:
        if user.username == username:
            result = user
            break
    return result

'''
Ingelogde gebruiker past eigen data succesvol aan.
'''
@patch("api.app.routers.profile.user_model.update_user", side_effect=fake_update_user)
@patch("api.auth_utils.user_model.get_user_by_username", return_value=get_fake_user("alice"))
def test_update_own_profile_success(fake_update, fake_user):
    payload = {"email": "newalice@example.com"}
    response = client.put("/update_profile", headers=valid_headers, json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "Profile updated" in data["message"]

'''
Als gebruiker niet ingelogd is en probeert aan te passen.
'''
@patch("api.app.routers.profile.user_model.update_user", side_effect=fake_update_user)
@patch("api.auth_utils.user_model.get_user_by_username", return_value=get_fake_user("alice"))
def test_update_profile_not_authorized(fake_update, fake_user):
    payload = {"email": "newalice@example.com"}
    response = client.put("/update_profile", headers=invalid_headers, json=payload)
    assert response.status_code == 401
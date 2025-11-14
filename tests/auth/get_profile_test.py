from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from unittest.mock import patch
import jwt
from api.datatypes.user import User

with patch("psycopg2.connect"):
    from api.main import app
    from api.auth_utils import SECRET_KEY, ALGORITHM, get_current_user



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

'''
Fake data
'''
def get_fake_user(username: str) -> User | None:
    users = [
        User(
            id=0,
            username="alice",
            password="password",  # plain text only for tests
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

client = TestClient(app)
'''
Haal profielgegevens op.
'''
@patch("api.auth_utils.user_model.get_user_by_username", return_value=get_fake_user("alice"))
def test_get_profile_when_authorized(fake_user):
    response = client.get("/profile", headers=valid_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "alice"

'''
Kijken of gebruiker is ingelogd.
'''
def test_get_profile_not_authorized():
    response = client.get("/profile", headers=invalid_headers)
    assert response.status_code == 401

'''
Controleer of de profieldata compleet is.
'''
@patch("api.auth_utils.user_model.get_user_by_username", return_value=get_fake_user("alice"))
def test_get_profile_data_is_complete(fake_user):
    response = client.get("/profile", headers=valid_headers)
    data = response.json()
    expected_keys = {"username", "email", "name", "role"}
    assert expected_keys.issubset(data.keys())

'''
Logout is de gebruiker ingelogd?
'''
@patch("api.auth_utils.user_model.get_user_by_username", return_value=get_fake_user("alice"))
def test_logout_when_logged_in(fake_user):
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
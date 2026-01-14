from datetime import date
from fastapi.testclient import TestClient
from api.datatypes.user import User, UserRole
from api.main import app
from api.models.user_model import UserModel
from api.tests.conftest import get_last_uid
from api.utilities.Hasher import hash_string

client = TestClient(app)

def test_create_new_user():
    user_model: UserModel = UserModel()
    fake_user = {
        "username": "test_user",
        "password": "Waddap",
        "name": "waddap",
        "email": "waddap@gmail.com",
        "phone": "1234567890",
        "birth_year": "2003",
    }
    response = client.post("/register", json=fake_user)
    assert response.status_code == 201
    user: User = user_model.get_user_by_username("test_user")
    assert not user.old_hash
    assert "$argon2" in user.password


def test_convert_old_user(client, client_with_token):
    user_model: UserModel = UserModel()
    password = hash_string("password", False)
    user = User(
        username="username",
        password=password,
        email="email",
        name="name",
        phone="phone",
        birth_year=2001,
        id=get_last_uid(client_with_token) + 1,
        created_at=date.today(),
        role=UserRole.USER,
        old_hash=True
    )
    user_model.create_user_debug(user)
    fake_user = {
        "username": "username",
        "password": "password"
    }
    response = client.post("/login", json=fake_user)
    assert response.status_code == 200
    converted_user: User = user_model.get_user_by_username("username")
    assert not converted_user.old_hash
    assert "$argon2" in converted_user.password

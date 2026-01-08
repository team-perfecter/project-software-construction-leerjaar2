"""
this file contains all tests related to post user endpoints.
"""

from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_register_not_all_field_filled(client):
    """Attempts to register a user with missing required fields.

    Args:
        client: TestClient instance for making requests.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 422.
    """
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
    """Registers a new user successfully with all required fields.

    Args:
        client: TestClient instance for making requests.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 201.
    """
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
    """Attempts to register a user with an already existing username.

    Args:
        client: TestClient instance for making requests.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 409.
    """
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
    """Creates a new user as a superadmin successfully.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 201.
    """
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
    """Attempts to create a user that already exists.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 409.
    """
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
    """Logs in an existing user successfully.

    Args:
        client: TestClient instance for making requests.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 200.
    """
    fake_user = {
        "username": "superadmin",
        "password": "admin123",
    }
    response = client.post("/login", json=fake_user)
    assert response.status_code == 200


def test_login_wrong_password(client):
    """Attempts to log in with an incorrect password.

    Args:
        client: TestClient instance for making requests.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 401.
    """
    fake_user = {
        "username": "superadmin",
        "password": "wrong",
    }
    response = client.post("/login", json=fake_user)
    assert response.status_code == 401


def test_login_not_existing_username(client):
    """Attempts to log in with a username that does not exist.

    Args:
        client: TestClient instance for making requests.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 404.
    """
    fake_user = {
        "username": "wrong",
        "password": "wrong",
    }
    response = client.post("/login", json=fake_user)
    assert response.status_code == 404


def test_logout(client_with_token):
    """Logs out a currently authenticated user successfully.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 200.
    """
    client, headers = client_with_token("user")
    response = client.post("/logout", headers=headers)
    assert response.status_code == 200


def test_logout_without_a_login(client):
    """Attempts to log out without being logged in.

    Args:
        client: TestClient instance for making requests.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 401.
    """
    response = client.post("/logout")
    assert response.status_code == 401

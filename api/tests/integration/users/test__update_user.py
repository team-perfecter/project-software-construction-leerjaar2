"""
this file contains all tests related to put user endpoints.
"""

from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_update_profile(client_with_token):
    """Updates the profile of the authenticated user successfully.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 200.
    """
    client, headers = client_with_token("user")
    fake_user = {
        "username": "waddapjes",
    }
    response = client.put("/update_profile", json=fake_user, headers=headers)
    assert response.status_code == 200

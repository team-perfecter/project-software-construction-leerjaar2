"""
this file contains all tests related to delete user endpoints.
"""

from api.tests.conftest import get_last_uid


def test_delete_user(client_with_token):
    """Deletes an existing user successfully with superadmin privileges.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 200.
    """
    user_id = get_last_uid(client_with_token)
    client, headers = client_with_token("superadmin")
    response = client.delete(f"/users/{user_id}", headers=headers)
    assert response.status_code == 200


def test_delete_user_that_doesnt_exist(client_with_token):
    """Attempts to delete a user that does not exist.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 404.
    """
    client, headers = client_with_token("superadmin")
    response = client.delete("/users/99999", headers=headers)
    assert response.status_code == 404

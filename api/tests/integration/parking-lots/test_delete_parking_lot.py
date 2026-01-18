"""
this file contains all tests related to delete parking lots endpoints.
"""

from api.tests.conftest import get_last_pid


# Tests voor DELETE /parking-lots/{id}
def test_delete_parking_lot_success(client_with_token):
    """Deletes an existing parking lot successfully.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the parking lot is not deleted successfully or response data is invalid.
    """
    superadmin_client, headers = client_with_token("superadmin")
    parking_lot_id = get_last_pid(superadmin_client)
    response = superadmin_client.delete(f"/parking-lots/{parking_lot_id}/force", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)


def test_delete_parking_lot_not_found(client_with_token):
    """Attempts to delete a non-existing parking lot.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 404.
    """
    superadmin_client, headers = client_with_token("superadmin")
    response = superadmin_client.delete(f"/parking-lots/999999/force", headers=headers)
    assert response.status_code == 404


def test_delete_parking_lot_unauthorized(client):
    """Attempts to delete a parking lot without authentication.

    Args:
        client: Unauthenticated test client.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 401.
    """
    parking_lot_id = get_last_pid(client)
    response = client.delete(f"/parking-lots/{parking_lot_id}/force")
    assert response.status_code == 401


def test_delete_parking_lot_forbidden(client_with_token):
    """Attempts to delete a parking lot with insufficient permissions.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 403.
    """
    user_client, headers = client_with_token("user")
    parking_lot_id = get_last_pid(user_client)
    response = user_client.delete(f"/parking-lots/{parking_lot_id}/force", headers=headers)
    assert response.status_code == 403


def test_delete_parking_lot_invalid_id(client_with_token):
    """Attempts to delete a parking lot using an invalid ID format.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 400, 404, or 422.
    """
    superadmin_client, headers = client_with_token("superadmin")
    invalid_id = "abc"
    response = superadmin_client.delete(f"/parking-lots/{invalid_id}/force", headers=headers)
    assert response.status_code in [400, 404, 422]

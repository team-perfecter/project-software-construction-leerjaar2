"""
this file contains all tests related to delete vehicle endpoints.
"""

import pytest
from api.tests.conftest import get_last_vid


# Test dat een gebruiker zijn eigen vehicle kan verwijderen
@pytest.mark.asyncio
def test_delete_vehicle_success(client_with_token):
    """Deletes a vehicle successfully when requested by an authorized user.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the vehicle is not deleted successfully or the response message is incorrect.
    """
    client, headers = client_with_token("superadmin")

    vehicle_id = get_last_vid(client_with_token)

    response = client.delete(
        f"/vehicles/delete/{vehicle_id}",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Vehicle succesfully deleted"


# Test verwijderen van een niet-bestaand vehicle
@pytest.mark.asyncio
def test_delete_vehicle_not_found(client_with_token):
    """Attempts to delete a vehicle that does not exist.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 404.
    """
    client, headers = client_with_token("superadmin")

    response = client.delete(
        "/vehicles/delete/999999",
        headers=headers,
    )

    assert response.status_code == 404


# Test dat een niet-ingelogde gebruiker geen vehicle kan verwijderen
@pytest.mark.asyncio
def test_delete_vehicle_unauthorized(client):
    """Attempts to delete a vehicle without authentication.

    Args:
        client: Unauthenticated test client.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 401.
    """
    response = client.delete("/vehicles/delete/1")
    assert response.status_code == 401


# Test wat er gebeurt als de gebruiker niet is ingelogd
def test_delete_vehicle_not_logged_in(client):
    """Attempts to delete a vehicle when the user is not logged in.

    Args:
        client: Unauthenticated test client.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 401.
    """
    response = client.delete("/vehicles/delete/1")
    assert response.status_code == 401

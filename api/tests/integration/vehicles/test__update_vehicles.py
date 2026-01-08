"""
this file contains all tests related to put vehicle endpoints.
"""

import pytest
from api.tests.conftest import get_last_vid


# Test dat een gebruiker zijn eigen vehicle succesvol kan updaten
@pytest.mark.asyncio
def test_update_vehicle_success(client_with_token):
    """Updates an existing vehicle successfully for an authorized user.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the vehicle is not updated successfully or the response message is incorrect.
    """
    client, headers = client_with_token("superadmin")
    vehicle_id = get_last_vid(client_with_token)
    updated_vehicle = {
        "license_plate": "UPDATED123",
        "make": "Tesla",
        "model": "Model 3",
        "color": "Red",
        "year": 2024,
    }

    response = client.put(
        f"/vehicles/update/{vehicle_id}",
        json=updated_vehicle,
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Vehicle succesfully updated"


# Test update van een niet-bestaand vehicle
@pytest.mark.asyncio
def test_update_vehicle_not_found(client_with_token):
    """Attempts to update a vehicle that does not exist.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 404.
    """
    client, headers = client_with_token("superadmin")

    updated_vehicle = {
        "license_plate": "DOESNOTEXIST",
        "make": "BMW",
        "model": "X5",
        "color": "Black",
        "year": 2022,
    }

    response = client.put(
        "/vehicles/update/999999",
        json=updated_vehicle,
        headers=headers,
    )

    assert response.status_code == 404


# Test dat een niet-ingelogde gebruiker geen vehicle kan updaten
@pytest.mark.asyncio
def test_update_vehicle_unauthorized(client):
    """Attempts to update a vehicle without authentication.

    Args:
        client: Unauthenticated test client.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 401.
    """
    updated_vehicle = {
        "license_plate": "NOAUTH",
        "make": "Ford",
        "model": "Focus",
        "color": "Blue",
        "year": 2020,
    }

    response = client.put(
        "/vehicles/update/1",
        json=updated_vehicle,
    )

    assert response.status_code == 401


# Test wat er gebeurt als de gebruiker niet is ingelogd
def test_update_vehicle_not_logged_in(client):
    """Attempts to update a vehicle when the user is not logged in.

    Args:
        client: Unauthenticated test client.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 401.
    """
    response = client.put("/vehicles/update/1", json={})
    assert response.status_code == 401

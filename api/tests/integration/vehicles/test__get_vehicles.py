"""
this file contains all tests related to get vehicle endpoints.
"""

import pytest
from api.tests.conftest import get_last_vid


@pytest.mark.asyncio
def test_get_all_vehicles(client_with_token):
    """Retrieves all vehicles for an authenticated user.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 200 or no vehicles are returned.
    """
    client, headers = client_with_token("superadmin")
    response = client.get("/vehicles", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


# Test dat een ingelogde gebruiker een specifieke vehicle kan ophalen
@pytest.mark.asyncio
def test_get_one_vehicle(client_with_token):
    """Retrieves a specific vehicle by ID for an authenticated user.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 200 or the vehicle data is incorrect.
    """
    client, headers = client_with_token("superadmin")
    vehicle_id = get_last_vid(client_with_token)

    response = client.get(f"/vehicles/{vehicle_id}", headers=headers)
    assert response.status_code == 200
    vehicle_data = response.json()
    assert vehicle_data["id"] == vehicle_id
    assert vehicle_data["license_plate"] == "ABC123"


# Test dat een ingelogde gebruiker alle vehicles kan ophalen van een specifieke user
@pytest.mark.asyncio
def test_get_vehicles_of_user(client_with_token):
    """Retrieves all vehicles belonging to a specific user as an admin.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 200 or the vehicle list is incorrect.
    """
    client, headers = client_with_token("superadmin")
    vehicle_id = get_last_vid(client_with_token)

    response = client.get("/vehicles/user/1", headers=headers)
    assert response.status_code == 200
    vehicles = response.json()

    vehicle_ids = [v["id"] for v in vehicles]
    assert vehicle_id in vehicle_ids


# Test dat een ingelogde gebruiker alle vehicles kan ophalen
def test_get_all_vehicles_logged_in(client_with_token):
    """Retrieves all vehicles when the user is logged in.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 200.
    """
    client, headers = client_with_token("superadmin")

    response = client.get("/vehicles", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) >= 1


# Test wat er gebeurt als de gebruiker niet is ingelogd
def test_get_all_vehicles_not_logged_in(client):
    """Attempts to retrieve all vehicles without authentication.

    Args:
        client: Unauthenticated test client.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 401.
    """
    response = client.get("/vehicles")
    assert response.status_code == 401


# Test wat er gebeurt als de gebruiker is ingelogd maar geen vehicles heeft
def test_get_all_vehicles_no_vehicles(client_with_token):
    """Retrieves vehicles when none exist for the authenticated user.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code or message is incorrect.
    """
    client, headers = client_with_token("superadmin")

    response = client.get("/vehicles", headers=headers)
    for vehicle in response.json():
        client.delete(f"/vehicles/delete/{vehicle['id']}", headers=headers)

    response = client.get("/vehicles", headers=headers)
    assert response.status_code == 404
    assert response.json()["message"] == "Vehicles not found"


# Test dat een ingelogde admin één specifieke vehicle kan ophalen
def test_get_one_vehicle_logged_in(client_with_token):
    """Retrieves a specific vehicle by ID as an authenticated admin.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 200 or ID does not match.
    """
    client, headers = client_with_token("superadmin")
    vehicle_id = get_last_vid(client_with_token)

    response = client.get(f"/vehicles/{vehicle_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == vehicle_id


# Test wat er gebeurt als een gebruiker niet is ingelogd
# Deze endpoint is momenteel publiek toegankelijk
def test_get_one_vehicle_not_logged_in(client):
    """Attempts to retrieve a vehicle without authentication.

    Args:
        client: Unauthenticated test client.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 404.
    """
    response = client.get("/vehicles/1")
    assert response.status_code == 404


# Test wat er gebeurt als een vehicle niet bestaat
def test_get_one_vehicle_not_found(client_with_token):
    """Attempts to retrieve a non-existing vehicle by ID.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 200 or 404.
    """
    client, headers = client_with_token("superadmin")

    response = client.get("/vehicles/999999", headers=headers)
    assert response.status_code in [200, 404]


# Test dat een admin alle vehicles van een specifieke gebruiker kan ophalen
def test_get_vehicles_of_user_as_admin(client_with_token):
    """Retrieves all vehicles for a specific user as an admin.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 200 or response is not a list.
    """
    client, headers = client_with_token("superadmin")

    response = client.get("/vehicles/user/1", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# Test wat er gebeurt als een admin vehicles ophaalt van een niet bestaande gebruiker
def test_get_vehicles_of_non_existing_user(client_with_token):
    """Attempts to retrieve vehicles for a non-existing user.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 404.
    """
    client, headers = client_with_token("superadmin")

    response = client.get("/vehicles/user/999999", headers=headers)
    assert response.status_code == 404


# Test wat er gebeurt als een normale gebruiker deze endpoint aanroept
def test_user_cannot_get_vehicles_of_other_user(client_with_token):
    """Attempts to retrieve another user's vehicles as a normal user.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 403.
    """
    client, headers = client_with_token("user")

    response = client.get("/vehicles/user/1", headers=headers)
    assert response.status_code == 403

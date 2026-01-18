from api.tests.conftest import get_last_vid, get_last_pid

# region get_sessions

def test_get_active_sessions(client_with_token):
    """
    Retrieves all active sessions as superadmin.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 200 or the data is not as expected.
    """
    client, headers = client_with_token("superadmin")
    response = client.get("/sessions/active", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "active_sessions" in data
    assert isinstance(data["active_sessions"], list)

def test_get_sessions_vehicle_success(client_with_token):
    """Test getting sessions for a specific vehicle"""
    client, headers = client_with_token("superadmin")
    vehicle_id = get_last_vid(client_with_token)

    response = client.get(f"/sessions/vehicle/{vehicle_id}", headers=headers)

    assert response.status_code == 200


def test_get_sessions_vehicle_not_owner(client_with_token):
    """
    Attempts to retrieve sessions for a vehicle not owned by the user.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 404.
    """
    client, headers = client_with_token("user")
    # Pak een vehicle van superadmin
    superadmin_client, superadmin_headers = client_with_token("superadmin")
    vehicles = superadmin_client.get("/vehicles", headers=superadmin_headers).json()
    assert vehicles, "No vehicles found for superadmin"
    vehicle_id = vehicles[0]["id"]
    response = client.get(f"/sessions/vehicle/{vehicle_id}", headers=headers)
    assert response.status_code == 404

def test_get_sessions_vehicle_unauthorized(client):
    """
    Attempts to retrieve sessions for a vehicle without authentication.

    Args:
        client: Unauthenticated test client.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 401.
    """
    vehicle_id = 1
    response = client.get(f"/sessions/vehicle/{vehicle_id}")
    assert response.status_code == 401

# endregion
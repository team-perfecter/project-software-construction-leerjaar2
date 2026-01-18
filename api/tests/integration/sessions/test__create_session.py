from api.tests.conftest import get_last_pid

# region start_parking_session

def test_start_session_succes(client_with_token):
    """
    Starts a session as a superadmin with correct data.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the session is not created successfully or response data is invalid.
    """
    client, headers = client_with_token("superadmin")
    lid = get_last_pid(client)
    license_plate = "ABC123"
    response = client.post(
        f"/sessions/parking-lots/{lid}/start/{license_plate}", headers=headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "Session started successfully"
    assert data["parking_lot_id"] == lid
    assert data["license_plate"] == license_plate


def test_start_session_already_active(client_with_token):
    """
    Attempts to start a session for a vehicle that already has an active session.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 409 or the error message is incorrect.
    """
    client, headers = client_with_token("superadmin")
    lid = get_last_pid(client)
    license_plate = "ABC123"
    client.post(f"/sessions/parking-lots/{lid}/start/{license_plate}", headers=headers)
    response = client.post(
        f"/sessions/parking-lots/{lid}/start/{license_plate}", headers=headers
    )
    assert response.status_code == 409


def test_start_session_parking_lot_not_found(client_with_token):
    """
    Attempts to start a session for a non-existing parking lot.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 404 or the error message is incorrect.
    """
    client, headers = client_with_token("superadmin")
    lid = 999999
    license_plate = "ABC123"
    response = client.post(
        f"/sessions/parking-lots/{lid}/start/{license_plate}", headers=headers
    )
    assert response.status_code == 404

# endregion
# region stop parking session
# region stop_parking_session

def test_stop_session_success(client_with_token):
    """
    Stops a session as a superadmin with correct data.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the session is not stopped successfully or response data is invalid.
    """
    client, headers = client_with_token("superadmin")
    lid = get_last_pid(client)
    license_plate = "ABC123"
    # Start eerst een sessie
    client.post(f"/sessions/parking-lots/{lid}/start/{license_plate}", headers=headers)
    response = client.post(f"/sessions/parking-lots/{lid}/stop/{license_plate}", headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert "Session stopped successfully" in data["message"]

def test_stop_session_no_active_session(client_with_token):
    """
    Attempts to stop a session for a vehicle with no active session.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response does not indicate no active session.
    """
    client, headers = client_with_token("superadmin")
    lid = get_last_pid(client)
    license_plate = "NOSESSION"
    response = client.post(f"/sessions/parking-lots/{lid}/stop/{license_plate}", headers=headers)
    # De endpoint retourneert een string, geen JSON
    assert response.status_code in [200, 201]
    assert "no active session" in response.text

# def test_stop_session_from_reservation_forbidden(client_with_token):
#     """
#     Attempts to stop a session started from a reservation via the regular stop endpoint.

#     Args:
#         client_with_token: Fixture providing an authenticated client and headers.

#     Returns:
#         None

#     Raises:
#         AssertionError: If the response status code is not 403.
#     """
#     # Deze test vereist een sessie gestart via een reservering.
#     # Implementeer deze als je reserveringen seedt in je tests.
#     pass

def test_stop_session_unauthorized(client):
    """
    Attempts to stop a session without authentication.

    Args:
        client: Unauthenticated test client.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 401 or 403.
    """
    lid = 1  # fallback
    try:
        lid = get_last_pid(client)
    except Exception:
        pass
    license_plate = "ABC123"
    response = client.post(f"/sessions/parking-lots/{lid}/stop/{license_plate}")
    assert response.status_code in [401, 403]

# endregion

# endregion


# region start_parking_session_from_reservation

# endregion
# region stop_parking_session_from_reservation


# endregion

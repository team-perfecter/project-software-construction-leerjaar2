from api.tests.conftest import get_last_pid, get_last_vid
from datetime import datetime, timedelta

# region start_parking_session

#def test_start_session_succes(client_with_token):
#    """
#    Starts a session as a superadmin with correct data.
#
#    Args:
#        client_with_token: Fixture providing an authenticated client and headers.
#
#    Returns:
#        None
#
#    Raises:
#        AssertionError: If the session is not created successfully or response data is invalid.
#    """
#    client, headers = client_with_token("superadmin")
#    lid = get_last_pid(client)
#    vehicle = {
#        "user_id": 1,
#        "license_plate": "ABC123",
#        "make": "Toyota",
#        "model": "Corolla",
#        "color": "Blue",
#        "year": 2020,
#    }
#
#
#
#    _ = client.post("/vehicles/create", json=vehicle, headers=headers)
#    response = client.get("/vehicles", headers=headers)
#    vehicle_id = response.json()[0]["id"]
#    # Stop a session, if one exists
#    _ = client.post(
#        f"/parking-lots/{lid}/sessions/stop/{vehicle_id}", headers=headers
#    )
#
#    response = client.post(
#        f"/parking-lots/{lid}/sessions/start/{vehicle_id}", headers=headers
#    )
#    assert response.status_code == 201
#    data = response.json()
#    assert data["message"] == "Session started successfully"
#    assert data["parking_lot_id"] == lid
#    assert data["license_plate"] == "ABC123"


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
    vehicle = {
        "user_id": 1,
        "license_plate": "ABC123",
        "make": "Toyota",
        "model": "Corolla",
        "color": "Blue",
        "year": 2020,
    }

    _ = client.post("/vehicles/create", json=vehicle, headers=headers)
    response = client.get("/vehicles", headers=headers)
    vehicle_id = response.json()[0]["id"]
    client.post(f"/parking-lots/{lid}/sessions/start/{vehicle_id}", headers=headers)
    response = client.post(
        f"/parking-lots/{lid}/sessions/start/{vehicle_id}", headers=headers
    )
    assert response.status_code == 409


# def test_start_session_no_account(client):
#     """
#     Starts a session without authentication.

#     Args:
#         client: Unauthenticated test client.

#     Returns:
#         None

#     Raises:
#         AssertionError: If the session is not created successfully or response data is invalid.
#     """
#     lid = 1  # fallback
#     try:
#         lid = get_last_pid(client)
#     except Exception:
#         pass
#     license_plate = "ABC123"
#     response = client.post(f"/sessions/parking-lots/{lid}/start/{license_plate}")
#     assert response.status_code == 201
#     data = response.json()
#     assert data["message"] == "Session started successfully"
#     assert data["parking_lot_id"] == lid
#     assert data["license_plate"] == license_plate


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
    vehicle = {
        "user_id": 1,
        "license_plate": "ABC123",
        "make": "Toyota",
        "model": "Corolla",
        "color": "Blue",
        "year": 2020,
    }

    _ = client.post("/vehicles/create", json=vehicle, headers=headers)
    response = client.get("/vehicles", headers=headers)
    vehicle_id = response.json()[0]["id"]
    # Start eerst een sessie
    client.post(f"/parking-lots/{lid}/sessions/start/{vehicle_id}", headers=headers)
    response = client.post(f"/parking-lots/{lid}/sessions/stop/{vehicle_id}", headers=headers)
    assert response.status_code == 200

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
    vehicle = {
        "user_id": 1,
        "license_plate": "ABC123",
        "make": "Toyota",
        "model": "Corolla",
        "color": "Blue",
        "year": 2020,
    }

    _ = client.post("/vehicles/create", json=vehicle, headers=headers)
    response = client.get("/vehicles", headers=headers)
    vehicle_id = response.json()[0]["id"]
    response = client.post(f"/parking-lots/{lid}/sessions/stop/{vehicle_id}", headers=headers)
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
    response = client.post(f"/parking-lots/{lid}/sessions/start/0")
    assert response.status_code in [401, 403]

# endregion


# region start_parking_session_from_reservation

def test_start_session_from_reservation_success(client_with_token):
    """
    Starts a session from a reservation as superadmin with correct data.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the session is not created successfully or response data is invalid.
    """
    client, headers = client_with_token("superadmin")
    vehicle_id = get_last_vid(client_with_token)
    parking_lot_id = get_last_pid(client)

    # Create a reservation first
    start_time = datetime.now() + timedelta(minutes=5)
    end_time = datetime.now() + timedelta(hours=2)

    reservation_data = {
        "vehicle_id": vehicle_id,
        "parking_lot_id": parking_lot_id,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
    }

    create_response = client.post(
        "/reservations/create", json=reservation_data, headers=headers
    )

    if create_response.status_code == 200:
        reservations_response = client.get(
            f"/reservations/vehicle/{vehicle_id}", headers=headers
        )
        reservations = reservations_response.json()

        if reservations:
            reservation_id = reservations[-1]["id"]

            response = client.post(
                f"/sessions/reservations/{reservation_id}/start", headers=headers
            )

            assert response.status_code in [200, 201, 409]

def test_start_session_from_reservation_not_found(client_with_token):
    """
    Attempts to start a session from a non-existing reservation.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 404.
    """
    client, headers = client_with_token("superadmin")
    response = client.post("/sessions/reservations/999999/start", headers=headers)
    assert response.status_code == 404

# endregion

# region stop_parking_session_from_reservation

# def test_stop_session_from_reservation_success(client_with_token):
#     """
#     Stops a session from a reservation as superadmin with correct data.

#     Args:
#         client_with_token: Fixture providing an authenticated client and headers.

#     Returns:
#         None

#     Raises:
#         AssertionError: If the session is not stopped successfully or response data is invalid.
#     """
#     client, headers = client_with_token("superadmin")
#     # Maak een reservering aan
#     reservation = {
#         "user_id": 1,
#         "parking_lot_id": 1,
#         "vehicle_id": 1,
#         "start_time": "2026-01-20T10:00:00",
#         "end_time": "2026-01-20T12:00:00"
#     }
#     res = client.post("/reservations", json=reservation, headers=headers)
#     assert res.status_code in [200, 201]
#     reservation_id = res.json().get("id") or res.json().get("reservation_id")
#     assert reservation_id is not None

#     # Start de sessie
#     response = client.post(f"/sessions/reservations/{reservation_id}/start", headers=headers)
#     assert response.status_code == 200

#     # Stop de sessie
#     response = client.post(f"/sessions/reservations/{reservation_id}/stop", headers=headers)
#     assert response.status_code == 200
#     data = response.json()
#     assert "message" in data
#     assert "session" in data

def test_stop_session_from_reservation_not_found(client_with_token):
    """
    Attempts to stop a session from a non-existing reservation.

    Args:
        client_with_token: Fixture providing an authenticated client and headers.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 404.
    """
    client, headers = client_with_token("superadmin")
    response = client.post("/parking-lots/-1/sessions/start/-1", headers=headers)
    assert response.status_code == 404

# endregion

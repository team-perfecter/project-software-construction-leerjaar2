import pytest
from datetime import datetime, timedelta
from api.tests.conftest import get_last_vid, get_last_pid


def create_reservation_and_start_session(
    client,
    headers,
    vehicle_id,
    parking_lot_id,
    start_offset_hours=1,
    end_offset_hours=3,
):
    """Helper function to create a reservation and start a session"""
    start_time = datetime.now() + timedelta(hours=start_offset_hours)
    end_time = datetime.now() + timedelta(hours=end_offset_hours)

    reservation_data = {
        "vehicle_id": vehicle_id,
        "parking_lot_id": parking_lot_id,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
    }

    create_response = client.post(
        "/reservations/create", json=reservation_data, headers=headers
    )

    if create_response.status_code != 200:
        return None, None

    reservations_response = client.get(
        f"/reservations/vehicle/{vehicle_id}", headers=headers
    )
    reservations = reservations_response.json()

    if not reservations:
        return None, None

    reservation_id = reservations[-1]["id"]

    # Start the session
    start_response = client.post(
        f"/sessions/reservations/{reservation_id}/start", headers=headers
    )

    return reservation_id, start_response.status_code


# region POST /parking-lots/{lid}/sessions/start
def test_start_session_success(client_with_token):
    """Test successfully starting a parking session"""
    client, headers = client_with_token("superadmin")
    vehicle_id = get_last_vid(client_with_token)
    parking_lot_id = get_last_pid(client)

    response = client.post(
        f"/parking-lots/{parking_lot_id}/sessions/start?vehicle_id={vehicle_id}",
        headers=headers,
    )

    assert response.status_code in [
        201,
        209,
    ]  # 201 for new session, 209 if already exists
    data = response.json()
    assert "message" in data


def test_start_session_parking_lot_not_found(client_with_token):
    """Test starting session with non-existent parking lot"""
    client, headers = client_with_token("superadmin")
    vehicle_id = get_last_vid(client_with_token)

    response = client.post(
        f"/parking-lots/99999/sessions/start?vehicle_id={vehicle_id}",
        headers=headers,
    )

    assert response.status_code == 404


def test_start_session_vehicle_not_found(client_with_token):
    """Test starting session with non-existent vehicle"""
    client, headers = client_with_token("superadmin")
    parking_lot_id = get_last_pid(client)

    response = client.post(
        f"/parking-lots/{parking_lot_id}/sessions/start?vehicle_id=99999",
        headers=headers,
    )

    assert response.status_code == 404


def test_start_session_vehicle_not_owned(client_with_token):
    """Test starting session with vehicle that doesn't belong to user"""
    superadmin_client, superadmin_headers = client_with_token("superadmin")
    parking_lot_id = get_last_pid(superadmin_client)

    # Get superadmin's vehicle
    vehicle_id = get_last_vid(client_with_token)

    # Try to start session as regular user with superadmin's vehicle
    user_client, user_headers = client_with_token("user")
    response = user_client.post(
        f"/parking-lots/{parking_lot_id}/sessions/start?vehicle_id={vehicle_id}",
        headers=user_headers,
    )

    assert response.status_code == 403
    data = response.json()
    assert "detail" in data
    assert data["detail"]["error"] == "Forbidden"
    assert "does not belong to current user" in data["detail"]["message"]


def test_start_session_no_authentication(client):
    """Test starting session without authentication"""
    response = client.post("/parking-lots/1/sessions/start?vehicle_id=1")

    assert response.status_code == 401


def test_start_session_invalid_parking_lot_id(client_with_token):
    """Test starting session with invalid parking lot ID format"""
    client, headers = client_with_token("superadmin")
    vehicle_id = get_last_vid(client_with_token)

    response = client.post(
        f"/parking-lots/invalid/sessions/start?vehicle_id={vehicle_id}",
        headers=headers,
    )

    assert response.status_code == 422


def test_start_session_invalid_vehicle_id(client_with_token):
    """Test starting session with invalid vehicle ID format"""
    client, headers = client_with_token("superadmin")
    parking_lot_id = get_last_pid(client)

    response = client.post(
        f"/parking-lots/{parking_lot_id}/sessions/start?vehicle_id=invalid",
        headers=headers,
    )

    assert response.status_code == 422


# endregion


# region POST /parking-lots/{lid}/sessions/stop
def test_stop_session_success(client_with_token):
    """Test successfully stopping a parking session"""
    client, headers = client_with_token("superadmin")
    vehicle_id = get_last_vid(client_with_token)
    parking_lot_id = get_last_pid(client)

    # Start a session first
    client.post(
        f"/parking-lots/{parking_lot_id}/sessions/start?vehicle_id={vehicle_id}",
        headers=headers,
    )

    # Stop the session
    response = client.post(
        f"/parking-lots/{parking_lot_id}/sessions/stop?vehicle_id={vehicle_id}",
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert "message" in data


def test_stop_session_from_reservation_via_regular_endpoint(client_with_token):
    """Test that stopping a reservation session via regular endpoint returns 403"""
    client, headers = client_with_token("superadmin")
    vehicle_id = get_last_vid(client_with_token)
    parking_lot_id = get_last_pid(client)

    # Stop any existing session first
    client.post(
        f"/parking-lots/{parking_lot_id}/sessions/stop?vehicle_id={vehicle_id}",
        headers=headers,
    )

    # Create reservation and start session
    reservation_id, start_status = create_reservation_and_start_session(
        client,
        headers,
        vehicle_id,
        parking_lot_id,
        start_offset_hours=50,
        end_offset_hours=52,
    )

    if reservation_id and start_status in [200, 201]:
        # Try to stop via regular endpoint - should fail with 403
        response = client.post(
            f"/parking-lots/{parking_lot_id}/sessions/stop?vehicle_id={vehicle_id}",
            headers=headers,
        )

        assert response.status_code == 403
        data = response.json()
        assert "detail" in data
        assert "reservation" in data["detail"].lower()


def test_stop_session_no_authentication(client):
    """Test stopping session without authentication"""
    response = client.post("/parking-lots/1/sessions/stop?vehicle_id=1")

    assert response.status_code == 401


def test_stop_session_invalid_parking_lot_id(client_with_token):
    """Test stopping session with invalid parking lot ID format"""
    client, headers = client_with_token("superadmin")
    vehicle_id = get_last_vid(client_with_token)

    response = client.post(
        f"/parking-lots/invalid/sessions/stop?vehicle_id={vehicle_id}",
        headers=headers,
    )

    assert response.status_code == 422


def test_stop_session_invalid_vehicle_id(client_with_token):
    """Test stopping session with invalid vehicle ID format"""
    client, headers = client_with_token("superadmin")
    parking_lot_id = get_last_pid(client)

    response = client.post(
        f"/parking-lots/{parking_lot_id}/sessions/stop?vehicle_id=invalid",
        headers=headers,
    )

    assert response.status_code == 422


# endregion


# region POST /sessions/reservations/{reservation_id}/start
def test_start_session_from_reservation_success(client_with_token):
    """Test starting session from a reservation"""
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


def test_start_session_from_reservation_already_exists(client_with_token):
    """Test starting session when one already exists for this reservation (409)"""
    client, headers = client_with_token("superadmin")
    vehicle_id = get_last_vid(client_with_token)
    parking_lot_id = get_last_pid(client)

    # Stop any existing session first
    client.post(
        f"/parking-lots/{parking_lot_id}/sessions/stop?vehicle_id={vehicle_id}",
        headers=headers,
    )

    # Create reservation and start session
    reservation_id, start_status = create_reservation_and_start_session(
        client,
        headers,
        vehicle_id,
        parking_lot_id,
        start_offset_hours=60,
        end_offset_hours=62,
    )

    if reservation_id and start_status in [200, 201]:
        # Try to start again - should fail with 409
        response = client.post(
            f"/sessions/reservations/{reservation_id}/start",
            headers=headers,
        )

        assert response.status_code == 409
        data = response.json()
        assert "detail" in data
        assert "already exists" in data["detail"].lower()


def test_start_session_from_reservation_not_found(client_with_token):
    """Test starting session from non-existent reservation"""
    client, headers = client_with_token("superadmin")

    response = client.post(
        "/sessions/reservations/99999/start",
        headers=headers,
    )

    assert response.status_code == 404


def test_start_session_from_reservation_not_owned(client_with_token):
    """Test starting session from reservation not owned by user"""
    superadmin_client, superadmin_headers = client_with_token("superadmin")
    vehicle_id = get_last_vid(client_with_token)
    parking_lot_id = get_last_pid(superadmin_client)

    start_time = datetime.now() + timedelta(hours=5)
    end_time = datetime.now() + timedelta(hours=7)

    reservation_data = {
        "vehicle_id": vehicle_id,
        "parking_lot_id": parking_lot_id,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
    }

    create_response = superadmin_client.post(
        "/reservations/create", json=reservation_data, headers=superadmin_headers
    )

    if create_response.status_code == 200:
        reservations_response = superadmin_client.get(
            f"/reservations/vehicle/{vehicle_id}", headers=superadmin_headers
        )
        reservations = reservations_response.json()

        if reservations:
            reservation_id = reservations[-1]["id"]

            user_client, user_headers = client_with_token("user")
            response = user_client.post(
                f"/sessions/reservations/{reservation_id}/start",
                headers=user_headers,
            )

            assert response.status_code == 403


def test_start_session_from_reservation_no_authentication(client):
    """Test starting session from reservation without authentication"""
    response = client.post("/sessions/reservations/1/start")

    assert response.status_code == 401


def test_start_session_from_reservation_invalid_id(client_with_token):
    """Test starting session from reservation with invalid ID format"""
    client, headers = client_with_token("superadmin")

    response = client.post(
        "/sessions/reservations/invalid/start",
        headers=headers,
    )

    assert response.status_code == 422


# endregion


# region POST /sessions/reservations/{reservation_id}/stop
def test_stop_session_from_reservation_success(client_with_token):
    """Test successfully stopping a session from reservation (no overtime)"""
    client, headers = client_with_token("superadmin")
    vehicle_id = get_last_vid(client_with_token)
    parking_lot_id = get_last_pid(client)

    # Stop any existing session first
    client.post(
        f"/parking-lots/{parking_lot_id}/sessions/stop?vehicle_id={vehicle_id}",
        headers=headers,
    )

    # Create reservation with future end_time (no overtime)
    reservation_id, start_status = create_reservation_and_start_session(
        client,
        headers,
        vehicle_id,
        parking_lot_id,
        start_offset_hours=1,
        end_offset_hours=10,  # End time is far in future
    )

    if reservation_id and start_status in [200, 201]:
        response = client.post(
            f"/sessions/reservations/{reservation_id}/stop",
            headers=headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        # Should indicate no extra cost since no overtime
        assert (
            "no extra cost" in data["message"].lower()
            or "stopped" in data["message"].lower()
        )


def test_stop_session_from_reservation_already_stopped(client_with_token):
    """Test stopping a session that is already stopped (409 or 404)"""
    client, headers = client_with_token("superadmin")
    vehicle_id = get_last_vid(client_with_token)
    parking_lot_id = get_last_pid(client)

    # Stop any existing session
    client.post(
        f"/parking-lots/{parking_lot_id}/sessions/stop?vehicle_id={vehicle_id}",
        headers=headers,
    )

    reservation_id, start_status = create_reservation_and_start_session(
        client,
        headers,
        vehicle_id,
        parking_lot_id,
        start_offset_hours=20,
        end_offset_hours=22,
    )

    if reservation_id and start_status in [200, 201]:
        # Stop first time
        first_stop = client.post(
            f"/sessions/reservations/{reservation_id}/stop",
            headers=headers,
        )

        if first_stop.status_code == 200:
            # Try to stop again - should be 404 or 409
            response = client.post(
                f"/sessions/reservations/{reservation_id}/stop",
                headers=headers,
            )

            # API returns 404 "No active session found" because stopped sessions
            # are not considered active, or 409 "Session already stopped"
            assert response.status_code in [404, 409]
            data = response.json()
            assert "detail" in data


def test_stop_session_from_reservation_not_found(client_with_token):
    """Test stopping session from non-existent reservation"""
    client, headers = client_with_token("superadmin")

    response = client.post(
        "/sessions/reservations/99999/stop",
        headers=headers,
    )

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_stop_session_from_reservation_no_active_session(client_with_token):
    """Test stopping when no session exists for the reservation (404)"""
    client, headers = client_with_token("superadmin")
    vehicle_id = get_last_vid(client_with_token)
    parking_lot_id = get_last_pid(client)

    # Create a reservation but don't start a session
    start_time = datetime.now() + timedelta(hours=30)
    end_time = datetime.now() + timedelta(hours=32)

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

            # Try to stop without starting - should return 404
            response = client.post(
                f"/sessions/reservations/{reservation_id}/stop",
                headers=headers,
            )

            assert response.status_code == 404
            assert "no active session" in response.json()["detail"].lower()


def test_stop_session_from_reservation_no_authentication(client):
    """Test stopping session from reservation without authentication"""
    response = client.post("/sessions/reservations/1/stop")

    assert response.status_code == 401


def test_stop_session_from_reservation_invalid_id(client_with_token):
    """Test stopping session from reservation with invalid ID format"""
    client, headers = client_with_token("superadmin")

    response = client.post(
        "/sessions/reservations/invalid/stop",
        headers=headers,
    )

    assert response.status_code == 422


def test_stop_session_from_reservation_negative_id(client_with_token):
    """Test stopping session with negative reservation ID"""
    client, headers = client_with_token("superadmin")

    response = client.post(
        "/sessions/reservations/-1/stop",
        headers=headers,
    )

    assert response.status_code == 404


def test_stop_session_from_reservation_zero_id(client_with_token):
    """Test stopping session with zero reservation ID"""
    client, headers = client_with_token("superadmin")

    response = client.post(
        "/sessions/reservations/0/stop",
        headers=headers,
    )

    assert response.status_code == 404


# endregion

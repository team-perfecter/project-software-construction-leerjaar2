import pytest
from unittest.mock import patch
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from api.main import app
from api.tests.conftest import (
    setup_reservation_prerequisites,
    create_test_vehicle,
    get_last_pid,
)

client = TestClient(app)


def test_create_reservation_success(client_with_token):
    """Test: Successfully create a reservation"""
    client, headers, vehicle_id, parking_lot_id = setup_reservation_prerequisites(
        client_with_token, role="user", vehicle_plate="CREATE-SUCCESS"
    )

    reservation_data = {
        "vehicle_id": vehicle_id,
        "parking_lot_id": parking_lot_id,
        "start_time": (datetime.now() + timedelta(days=1)).isoformat(),
        "end_time": (datetime.now() + timedelta(days=2)).isoformat(),
    }

    response = client.post(
        "/reservations/create", json=reservation_data, headers=headers
    )
    assert response.status_code == 201

    data = response.json()
    assert "vehicle_id" in data
    assert "parking_lot_id" in data
    assert "start_time" in data
    assert "end_time" in data
    assert data["vehicle_id"] == vehicle_id
    assert data["parking_lot_id"] == parking_lot_id


def test_create_reservation_unauthorized(client):
    """Test: Create reservation without token"""
    reservation_data = {
        "vehicle_id": 1,
        "parking_lot_id": 1,
        "start_time": (datetime.now() + timedelta(days=1)).isoformat(),
        "end_time": (datetime.now() + timedelta(days=2)).isoformat(),
    }
    response = client.post("/reservations/create", json=reservation_data)
    assert response.status_code == 401


def test_create_reservation_missing_field(client_with_token):
    """Test: Create reservation with missing required fields"""
    client, headers = client_with_token("user")
    incomplete_data = {
        "vehicle_id": 1,
        "parking_lot_id": 1,
        # Missing start_time and end_time
    }
    response = client.post(
        "/reservations/create", json=incomplete_data, headers=headers
    )
    assert response.status_code == 422


def test_create_reservation_wrong_data_type(client_with_token):
    """Test: Create reservation with wrong data types"""
    client, headers = client_with_token("user")
    invalid_data = {
        "vehicle_id": "not_a_number",
        "parking_lot_id": "invalid",
        "start_time": "invalid_date",
        "end_time": "invalid_date",
    }
    response = client.post("/reservations/create", json=invalid_data, headers=headers)
    assert response.status_code == 422


def test_create_reservation_nonexistent_parking_lot(client_with_token):
    """Test: Create reservation with non-existent parking lot"""
    client, headers, vehicle_id, _ = setup_reservation_prerequisites(
        client_with_token, vehicle_plate="NO-PARKING"
    )

    reservation_data = {
        "vehicle_id": vehicle_id,
        "parking_lot_id": 99999,
        "start_time": (datetime.now() + timedelta(days=1)).isoformat(),
        "end_time": (datetime.now() + timedelta(days=2)).isoformat(),
    }
    response = client.post(
        "/reservations/create", json=reservation_data, headers=headers
    )
    assert response.status_code == 404


def test_create_reservation_nonexistent_vehicle(client_with_token):
    """Test: Create reservation with non-existent vehicle"""
    client, headers = client_with_token("user")
    parking_lot_id = get_last_pid(client)

    reservation_data = {
        "vehicle_id": 99999,
        "parking_lot_id": parking_lot_id,
        "start_time": (datetime.now() + timedelta(days=1)).isoformat(),
        "end_time": (datetime.now() + timedelta(days=2)).isoformat(),
    }
    response = client.post(
        "/reservations/create", json=reservation_data, headers=headers
    )
    assert response.status_code == 404


def test_create_reservation_past_date(client_with_token):
    """Test: Create reservation with past start date"""
    client, headers, vehicle_id, parking_lot_id = setup_reservation_prerequisites(
        client_with_token, vehicle_plate="PAST-DATE"
    )

    reservation_data = {
        "vehicle_id": vehicle_id,
        "parking_lot_id": parking_lot_id,
        "start_time": (datetime.now() - timedelta(days=1)).isoformat(),
        "end_time": (datetime.now() + timedelta(days=1)).isoformat(),
    }
    response = client.post(
        "/reservations/create", json=reservation_data, headers=headers
    )
    assert response.status_code == 403


def test_create_reservation_invalid_date_range(client_with_token):
    """Test: Create reservation with end date before start date"""
    client, headers, vehicle_id, parking_lot_id = setup_reservation_prerequisites(
        client_with_token, vehicle_plate="INVALID-RANGE"
    )

    reservation_data = {
        "vehicle_id": vehicle_id,
        "parking_lot_id": parking_lot_id,
        "start_time": (datetime.now() + timedelta(days=2)).isoformat(),
        "end_time": (datetime.now() + timedelta(days=1)).isoformat(),
    }
    response = client.post(
        "/reservations/create", json=reservation_data, headers=headers
    )
    assert response.status_code == 403


def test_create_reservation_same_start_end_time(client_with_token):
    """Test: Create reservation with same start and end date"""
    client, headers, vehicle_id, parking_lot_id = setup_reservation_prerequisites(
        client_with_token, vehicle_plate="SAME-DATE"
    )

    future_date = (datetime.now() + timedelta(days=1)).isoformat()

    reservation_data = {
        "vehicle_id": vehicle_id,
        "parking_lot_id": parking_lot_id,
        "start_time": future_date,
        "end_time": future_date,
    }
    response = client.post(
        "/reservations/create", json=reservation_data, headers=headers
    )
    assert response.status_code == 403


def test_create_reservation_conflicting_time(client_with_token):
    """Test: Create overlapping reservations for same vehicle"""
    client, headers, vehicle_id, parking_lot_id = setup_reservation_prerequisites(
        client_with_token, vehicle_plate="CONFLICT"
    )

    # Create first reservation
    first_reservation = {
        "vehicle_id": vehicle_id,
        "parking_lot_id": parking_lot_id,
        "start_time": (datetime.now() + timedelta(days=1)).isoformat(),
        "end_time": (datetime.now() + timedelta(days=3)).isoformat(),
    }
    first_response = client.post(
        "/reservations/create", json=first_reservation, headers=headers
    )

    if first_response.status_code == 201:
        # Try to create overlapping reservation
        second_reservation = {
            "vehicle_id": vehicle_id,
            "parking_lot_id": parking_lot_id,
            "start_time": (datetime.now() + timedelta(days=2)).isoformat(),
            "end_time": (datetime.now() + timedelta(days=4)).isoformat(),
        }
        second_response = client.post(
            "/reservations/create", json=second_reservation, headers=headers
        )
        assert second_response.status_code == 401


def test_create_multiple_non_overlapping_reservations(client_with_token):
    """Test: Create multiple non-overlapping reservations for same vehicle"""
    client, headers, vehicle_id, parking_lot_id = setup_reservation_prerequisites(
        client_with_token, vehicle_plate="MULTIPLE"
    )

    # First reservation
    first_data = {
        "vehicle_id": vehicle_id,
        "parking_lot_id": parking_lot_id,
        "start_time": (datetime.now() + timedelta(days=1)).isoformat(),
        "end_time": (datetime.now() + timedelta(days=2)).isoformat(),
    }
    first_response = client.post(
        "/reservations/create", json=first_data, headers=headers
    )
    assert first_response.status_code == 201

    first_data_response = first_response.json()
    assert first_data_response["vehicle_id"] == vehicle_id

    # Second reservation (non-overlapping)
    second_data = {
        "vehicle_id": vehicle_id,
        "parking_lot_id": parking_lot_id,
        "start_time": (datetime.now() + timedelta(days=3)).isoformat(),
        "end_time": (datetime.now() + timedelta(days=4)).isoformat(),
    }
    second_response = client.post(
        "/reservations/create", json=second_data, headers=headers
    )
    assert second_response.status_code == 201

    second_data_response = second_response.json()
    assert second_data_response["vehicle_id"] == vehicle_id


def test_create_reservation_one_minute_duration(client_with_token):
    """Test: Create reservation with very short duration (1 minute)"""
    client, headers, vehicle_id, parking_lot_id = setup_reservation_prerequisites(
        client_with_token, vehicle_plate="SHORT-DURATION"
    )

    start = datetime.now() + timedelta(hours=1)
    end = start + timedelta(minutes=1)

    reservation_data = {
        "vehicle_id": vehicle_id,
        "parking_lot_id": parking_lot_id,
        "start_time": start.isoformat(),
        "end_time": end.isoformat(),
    }
    response = client.post(
        "/reservations/create", json=reservation_data, headers=headers
    )
    assert response.status_code == 201

    data = response.json()
    response_start = datetime.fromisoformat(data["start_time"])
    response_end = datetime.fromisoformat(data["end_time"])
    duration = (response_end - response_start).total_seconds()
    assert duration == 60  # 1 minute


def test_create_reservation_one_year_duration(client_with_token):
    """Test: Create reservation with very long duration (1 year)"""
    client, headers, vehicle_id, parking_lot_id = setup_reservation_prerequisites(
        client_with_token, vehicle_plate="LONG-DURATION"
    )

    start = datetime.now() + timedelta(days=1)
    end = start + timedelta(days=365)

    reservation_data = {
        "vehicle_id": vehicle_id,
        "parking_lot_id": parking_lot_id,
        "start_time": start.isoformat(),
        "end_time": end.isoformat(),
    }
    response = client.post(
        "/reservations/create", json=reservation_data, headers=headers
    )
    assert response.status_code == 201


@pytest.mark.parametrize("role", ["user", "admin", "superadmin"])
def test_create_reservation_different_roles(client_with_token, role):
    """Test: Different user roles can create reservations"""
    client, headers, vehicle_id, parking_lot_id = setup_reservation_prerequisites(
        client_with_token, role=role, vehicle_plate=f"ROLE-{role.upper()}"
    )

    reservation_data = {
        "vehicle_id": vehicle_id,
        "parking_lot_id": parking_lot_id,
        "start_time": (datetime.now() + timedelta(days=1)).isoformat(),
        "end_time": (datetime.now() + timedelta(days=2)).isoformat(),
    }
    response = client.post(
        "/reservations/create", json=reservation_data, headers=headers
    )
    assert response.status_code == 201

    data = response.json()
    assert data["vehicle_id"] == vehicle_id
    assert data["parking_lot_id"] == parking_lot_id


@patch(
    "api.app.routers.reservations.parkingLot_model.get_parking_lot_by_lid",
    return_value=None,
)
def test_create_reservation_parking_lot_not_found_mock(mock_get_lot, client_with_token):
    """Test: Mock parking lot not found"""
    client, headers = client_with_token("user")
    vehicle_id = create_test_vehicle(client, headers, "MOCK-NO-LOT")

    reservation_data = {
        "vehicle_id": vehicle_id,
        "parking_lot_id": 1,
        "start_time": (datetime.now() + timedelta(days=1)).isoformat(),
        "end_time": (datetime.now() + timedelta(days=2)).isoformat(),
    }
    response = client.post(
        "/reservations/create", json=reservation_data, headers=headers
    )
    assert response.status_code == 404
    mock_get_lot.assert_called_once_with(1)


@patch("api.app.routers.reservations.vehicle_model.get_one_vehicle", return_value=None)
def test_create_reservation_vehicle_not_found_mock(mock_get_vehicle, client_with_token):
    """Test: Mock vehicle not found"""
    client, headers = client_with_token("user")
    parking_lot_id = get_last_pid(client)

    reservation_data = {
        "vehicle_id": 1,
        "parking_lot_id": parking_lot_id,
        "start_time": (datetime.now() + timedelta(days=1)).isoformat(),
        "end_time": (datetime.now() + timedelta(days=2)).isoformat(),
    }
    response = client.post(
        "/reservations/create", json=reservation_data, headers=headers
    )
    assert response.status_code == 404
    mock_get_vehicle.assert_called_once_with(1)


@patch(
    "api.models.reservation_model.Reservation_model.create_reservation",
    side_effect=Exception("Database error"),
)
def test_create_reservation_server_error_mock(mock_create, client_with_token):
    """Test: Mock database error during creation"""
    client, headers, vehicle_id, parking_lot_id = setup_reservation_prerequisites(
        client_with_token, vehicle_plate="MOCK-ERROR"
    )

    reservation_data = {
        "vehicle_id": vehicle_id,
        "parking_lot_id": parking_lot_id,
        "start_time": (datetime.now() + timedelta(days=1)).isoformat(),
        "end_time": (datetime.now() + timedelta(days=2)).isoformat(),
    }
    response = client.post(
        "/reservations/create", json=reservation_data, headers=headers
    )
    assert response.status_code == 500


def test_create_reservation_exactly_now(client_with_token):
    """Test: Create reservation starting exactly now"""
    client, headers, vehicle_id, parking_lot_id = setup_reservation_prerequisites(
        client_with_token, vehicle_plate="NOW"
    )

    reservation_data = {
        "vehicle_id": vehicle_id,
        "parking_lot_id": parking_lot_id,
        "start_time": datetime.now().isoformat(),
        "end_time": (datetime.now() + timedelta(hours=1)).isoformat(),
    }
    response = client.post(
        "/reservations/create", json=reservation_data, headers=headers
    )
    assert response.status_code == 403


def test_create_reservation_one_second_future(client_with_token):
    """Test: Create reservation starting one second in the future"""
    client, headers, vehicle_id, parking_lot_id = setup_reservation_prerequisites(
        client_with_token, vehicle_plate="ONE-SECOND"
    )

    start = datetime.now() + timedelta(seconds=1)

    reservation_data = {
        "vehicle_id": vehicle_id,
        "parking_lot_id": parking_lot_id,
        "start_time": start.isoformat(),
        "end_time": (start + timedelta(hours=1)).isoformat(),
    }
    response = client.post(
        "/reservations/create", json=reservation_data, headers=headers
    )
    assert response.status_code == 201

    data = response.json()
    assert "start_time" in data
    assert "end_time" in data

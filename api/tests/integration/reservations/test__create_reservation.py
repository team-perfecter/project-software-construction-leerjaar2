import pytest
from datetime import datetime, timedelta
from api.tests.conftest import get_last_vid, get_last_pid


# region POST /reservations/create
def test_create_reservation_success(client_with_token):
    """Test successfully creating a reservation"""
    client, headers = client_with_token("user")
    vehicle_id = get_last_vid(client_with_token)
    parking_lot_id = get_last_pid(client)

    reservation_data = {
        "vehicle_id": vehicle_id,
        "parking_lot_id": parking_lot_id,
        "start_date": (datetime.now() + timedelta(hours=1)).isoformat(),
        "end_date": (datetime.now() + timedelta(hours=3)).isoformat(),
    }

    response = client.post(
        "/reservations/create", json=reservation_data, headers=headers
    )

    assert response.status_code == 200
    assert "message" in response.json()
    assert response.json()["message"] == "Reservation created successfully"


def test_create_reservation_parking_lot_not_found(client_with_token):
    """Test creating reservation with non-existent parking lot"""
    client, headers = client_with_token("user")
    vehicle_id = get_last_vid(client_with_token)

    reservation_data = {
        "vehicle_id": vehicle_id,
        "parking_lot_id": 99999,
        "start_date": (datetime.now() + timedelta(hours=1)).isoformat(),
        "end_date": (datetime.now() + timedelta(hours=3)).isoformat(),
    }

    response = client.post(
        "/reservations/create", json=reservation_data, headers=headers
    )

    assert response.status_code == 404
    assert "Parking lot does not exist" in response.json()["detail"]["message"]


def test_create_reservation_vehicle_not_found(client_with_token):
    """Test creating reservation with non-existent vehicle"""
    client, headers = client_with_token("user")
    parking_lot_id = get_last_pid(client)

    reservation_data = {
        "vehicle_id": 99999,
        "parking_lot_id": parking_lot_id,
        "start_date": (datetime.now() + timedelta(hours=1)).isoformat(),
        "end_date": (datetime.now() + timedelta(hours=3)).isoformat(),
    }

    response = client.post(
        "/reservations/create", json=reservation_data, headers=headers
    )

    assert response.status_code == 404
    assert "Vehicle does not exist" in response.json()["detail"]["message"]


def test_create_reservation_no_authentication(client):
    """Test creating reservation without authentication"""
    reservation_data = {
        "vehicle_id": 1,
        "parking_lot_id": 1,
        "start_date": (datetime.now() + timedelta(hours=1)).isoformat(),
        "end_date": (datetime.now() + timedelta(hours=3)).isoformat(),
    }

    response = client.post("/reservations/create", json=reservation_data)

    assert response.status_code == 401


def test_create_reservation_missing_fields(client_with_token):
    """Test creating reservation with missing required fields"""
    client, headers = client_with_token("user")

    reservation_data = {
        "vehicle_id": 1,
        "parking_lot_id": 1,
        # Missing start_date and end_date
    }

    response = client.post(
        "/reservations/create", json=reservation_data, headers=headers
    )

    assert response.status_code == 422


def test_create_reservation_invalid_date_format(client_with_token):
    """Test creating reservation with invalid date format"""
    client, headers = client_with_token("user")
    vehicle_id = get_last_vid(client_with_token)
    parking_lot_id = get_last_pid(client)

    reservation_data = {
        "vehicle_id": vehicle_id,
        "parking_lot_id": parking_lot_id,
        "start_date": "invalid-date",
        "end_date": "invalid-date",
    }

    response = client.post(
        "/reservations/create", json=reservation_data, headers=headers
    )

    assert response.status_code == 422


# endregion

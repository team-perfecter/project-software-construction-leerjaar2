import pytest
from datetime import datetime, timedelta
from api.tests.conftest import get_last_vid, get_last_pid


def test_create_reservation_success(client_with_token):
    """Test successfully creating a reservation"""
    client, headers = client_with_token("superadmin")
    vehicle_id = get_last_vid(client_with_token)
    parking_lot_id = get_last_pid(client)

    # The API expects datetime objects, not strings
    start_time = datetime.now() + timedelta(hours=1)
    end_time = datetime.now() + timedelta(hours=3)

    reservation_data = {
        "vehicle_id": vehicle_id,
        "parking_lot_id": parking_lot_id,
        "start_date": start_time.isoformat(),  # Use isoformat() with full datetime
        "end_date": end_time.isoformat(),
    }

    response = client.post(
        "/reservations/create", json=reservation_data, headers=headers
    )

    # The endpoint returns 200 with a message, not 201
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "Reservation created successfully"


def test_create_reservation_parking_lot_not_found(client_with_token):
    """Test creating reservation with non-existent parking lot"""
    client, headers = client_with_token("superadmin")
    vehicle_id = get_last_vid(client_with_token)

    start_time = datetime.now() + timedelta(hours=1)
    end_time = datetime.now() + timedelta(hours=3)

    reservation_data = {
        "vehicle_id": vehicle_id,
        "parking_lot_id": 99999,
        "start_date": start_time.isoformat(),
        "end_date": end_time.isoformat(),
    }

    response = client.post(
        "/reservations/create", json=reservation_data, headers=headers
    )

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "parking lot" in str(data["detail"]).lower()


def test_create_reservation_vehicle_not_found(client_with_token):
    """Test creating reservation with non-existent vehicle"""
    client, headers = client_with_token("superadmin")
    parking_lot_id = get_last_pid(client)

    start_time = datetime.now() + timedelta(hours=1)
    end_time = datetime.now() + timedelta(hours=3)

    reservation_data = {
        "vehicle_id": 99999,
        "parking_lot_id": parking_lot_id,
        "start_date": start_time.isoformat(),
        "end_date": end_time.isoformat(),
    }

    response = client.post(
        "/reservations/create", json=reservation_data, headers=headers
    )

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "vehicle" in str(data["detail"]).lower()


def test_create_reservation_no_authentication(client):
    """Test creating reservation without authentication"""
    start_time = datetime.now() + timedelta(hours=1)
    end_time = datetime.now() + timedelta(hours=3)

    reservation_data = {
        "vehicle_id": 1,
        "parking_lot_id": 1,
        "start_date": start_time.isoformat(),
        "end_date": end_time.isoformat(),
    }

    response = client.post("/reservations/create", json=reservation_data)

    assert response.status_code == 401


def test_create_reservation_missing_fields(client_with_token):
    """Test creating reservation with missing required fields"""
    client, headers = client_with_token("superadmin")

    reservation_data = {
        "vehicle_id": 1,
        # Missing parking_lot_id, start_date, end_date
    }

    response = client.post(
        "/reservations/create", json=reservation_data, headers=headers
    )

    assert response.status_code == 422


def test_create_reservation_invalid_date_format(client_with_token):
    """Test creating reservation with invalid date format"""
    client, headers = client_with_token("superadmin")
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

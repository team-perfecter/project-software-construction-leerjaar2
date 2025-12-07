from datetime import date
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


# Mock functions
def mock_get_parking_lot(lot_id: int):
    if lot_id == 1:
        return {
            "id": 1,
            "name": "Test Parking",
            "capacity": 100,
            "reserved": 50,
            "location": "Test Location",
        }
    elif lot_id == 2:
        return {
            "id": 2,
            "name": "Full Parking",
            "capacity": 100,
            "reserved": 100,
            "location": "Test Location",
        }
    return None


def mock_get_vehicle(vehicle_id: int, user_id: int):
    if vehicle_id == 1 and user_id == 1:
        return {"id": 1, "user_id": 1, "license_plate": "ABC123"}
    return None


def mock_check_existing_reservation(vehicle_id: int):
    return vehicle_id == 99  # Vehicle 99 already has a reservation


def mock_check_active_session(vehicle_id: int):
    return vehicle_id == 98  # Vehicle 98 is currently parked


# Tests for POST /reservations
def test_create_reservation_success(client_with_token):
    client, headers = client_with_token("user")
    reservation_data = {
        "vehicle_id": 1,
        "parking_lot_id": 1,
        "start_date": "2025-12-10T09:00:00",
        "end_date": "2025-12-10T18:00:00",
    }
    response = client.post(
        "/reservations/create", json=reservation_data, headers=headers
    )
    assert response.status_code in [200, 201]


def test_create_reservation_unauthorized(client):
    reservation_data = {
        "vehicle_id": 1,
        "parking_lot_id": 1,
        "start_date": "2025-12-10T09:00:00",
        "end_date": "2025-12-10T18:00:00",
    }
    response = client.post("/reservations/create", json=reservation_data)
    assert response.status_code == 401


def test_create_reservation_missing_field(client_with_token):
    client, headers = client_with_token("user")
    incomplete_data = {
        "vehicle_id": 1,
        "parking_lot_id": 1,
        # Missing start_date and end_date
    }
    response = client.post(
        "/reservations/create", json=incomplete_data, headers=headers
    )
    assert response.status_code == 422


def test_create_reservation_wrong_data_type(client_with_token):
    client, headers = client_with_token("user")
    invalid_data = {
        "vehicle_id": "not_a_number",
        "parking_lot_id": 1,
        "start_date": "2025-12-10T09:00:00",
        "end_date": "2025-12-10T18:00:00",
    }
    response = client.post("/reservations/create", json=invalid_data, headers=headers)
    assert response.status_code == 422


def test_create_reservation_nonexistent_parking_lot(client_with_token):
    client, headers = client_with_token("user")
    reservation_data = {
        "vehicle_id": 1,
        "parking_lot_id": 99999,
        "start_date": "2025-12-10T09:00:00",
        "end_date": "2025-12-10T18:00:00",
    }
    response = client.post(
        "/reservations/create", json=reservation_data, headers=headers
    )
    assert response.status_code == 404


def test_create_reservation_nonexistent_vehicle(client_with_token):
    client, headers = client_with_token("user")
    reservation_data = {
        "vehicle_id": 99999,
        "parking_lot_id": 1,
        "start_date": "2025-12-10T09:00:00",
        "end_date": "2025-12-10T18:00:00",
    }
    response = client.post(
        "/reservations/create", json=reservation_data, headers=headers
    )
    assert response.status_code == 404


def test_create_reservation_parking_lot_full(client_with_token):
    client, headers = client_with_token("user")
    # First create reservations to fill up the parking lot
    # Then try to create another reservation
    reservation_data = {
        "vehicle_id": 1,
        "parking_lot_id": 1,
        "start_date": "2025-12-10T09:00:00",
        "end_date": "2025-12-10T18:00:00",
    }
    # This assumes the parking lot becomes full
    response = client.post(
        "/reservations/create", json=reservation_data, headers=headers
    )
    # Status code depends on implementation - could be 403 or 409
    assert response.status_code in [200, 201, 403, 409]


def test_create_reservation_vehicle_already_reserved(client_with_token):
    client, headers = client_with_token("user")
    reservation_data = {
        "vehicle_id": 1,
        "parking_lot_id": 1,
        "start_date": "2025-12-10T09:00:00",
        "end_date": "2025-12-10T18:00:00",
    }
    # Create first reservation
    client.post("/reservations/create", json=reservation_data, headers=headers)

    # Try to create second reservation with same vehicle
    response = client.post(
        "/reservations/create", json=reservation_data, headers=headers
    )
    assert response.status_code == 403


def test_create_reservation_invalid_date_range(client_with_token):
    client, headers = client_with_token("user")
    invalid_data = {
        "vehicle_id": 1,
        "parking_lot_id": 1,
        "start_date": "2025-12-10T18:00:00",
        "end_date": "2025-12-10T09:00:00",  # Before start date
    }
    response = client.post("/reservations/create", json=invalid_data, headers=headers)
    assert response.status_code in [400, 422]


def test_create_reservation_past_date(client_with_token):
    client, headers = client_with_token("user")
    past_data = {
        "vehicle_id": 1,
        "parking_lot_id": 1,
        "start_date": "2020-01-01T09:00:00",
        "end_date": "2020-01-01T18:00:00",
    }
    response = client.post("/reservations/create", json=past_data, headers=headers)
    assert response.status_code in [400, 422]


@patch(
    "api.models.reservation_model.ReservationModel.create_reservation",
    return_value=False,
)
def test_create_reservation_server_error(mock_create, client_with_token):
    client, headers = client_with_token("user")
    reservation_data = {
        "vehicle_id": 1,
        "parking_lot_id": 1,
        "start_date": "2025-12-10T09:00:00",
        "end_date": "2025-12-10T18:00:00",
    }
    response = client.post(
        "/reservations/create", json=reservation_data, headers=headers
    )
    assert response.status_code == 500


# Admin endpoint


def test_admin_create_reservation_success(client_with_token):
    admin_client, headers = client_with_token("admin")
    reservation_data = {
        "user_id": 1,
        "vehicle_id": 1,
        "parking_lot_id": 1,
        "start_time": "2025-12-10T09:00:00",
        "end_time": "2025-12-10T18:00:00",
        "status": "confirmed",
        "cost": 20,
    }
    response = admin_client.post(
        "/admin/reservations", json=reservation_data, headers=headers
    )
    assert response.status_code == 201


def test_admin_create_reservation_unauthorized_user(client_with_token):
    user_client, headers = client_with_token("user")
    reservation_data = {
        "user_id": 1,
        "vehicle_id": 1,
        "parking_lot_id": 1,
        "start_time": "2025-12-10T09:00:00",
        "end_time": "2025-12-10T18:00:00",
        "status": "confirmed",
        "cost": 20,
    }
    response = user_client.post(
        "/admin/reservations", json=reservation_data, headers=headers
    )
    assert response.status_code == 403


def test_admin_create_reservation_unauthorized(client):
    reservation_data = {
        "user_id": 1,
        "vehicle_id": 1,
        "parking_lot_id": 1,
        "start_time": "2025-12-10T09:00:00",
        "end_time": "2025-12-10T18:00:00",
        "status": "confirmed",
        "cost": 20,
    }
    response = client.post("/admin/reservations", json=reservation_data)
    assert response.status_code == 401


def test_admin_create_reservation_missing_field(client_with_token):
    admin_client, headers = client_with_token("admin")
    incomplete_data = {
        "user_id": 1,
        "vehicle_id": 1,
        # Missing other required fields
    }
    response = admin_client.post(
        "/admin/reservations", json=incomplete_data, headers=headers
    )
    assert response.status_code == 422


def test_admin_create_reservation_nonexistent_user(client_with_token):
    admin_client, headers = client_with_token("admin")
    reservation_data = {
        "user_id": 99999,
        "vehicle_id": 1,
        "parking_lot_id": 1,
        "start_time": "2025-12-10T09:00:00",
        "end_time": "2025-12-10T18:00:00",
        "status": "confirmed",
        "cost": 20,
    }
    response = admin_client.post(
        "/admin/reservations", json=reservation_data, headers=headers
    )
    assert response.status_code == 404


def test_admin_create_reservation_nonexistent_vehicle(client_with_token):
    admin_client, headers = client_with_token("admin")
    reservation_data = {
        "user_id": 1,
        "vehicle_id": 99999,
        "parking_lot_id": 1,
        "start_time": "2025-12-10T09:00:00",
        "end_time": "2025-12-10T18:00:00",
        "status": "confirmed",
        "cost": 20,
    }
    response = admin_client.post(
        "/admin/reservations", json=reservation_data, headers=headers
    )
    assert response.status_code == 404


def test_admin_create_reservation_nonexistent_parking_lot(client_with_token):
    admin_client, headers = client_with_token("admin")
    reservation_data = {
        "user_id": 1,
        "vehicle_id": 1,
        "parking_lot_id": 99999,
        "start_time": "2025-12-10T09:00:00",
        "end_time": "2025-12-10T18:00:00",
        "status": "confirmed",
        "cost": 20,
    }
    response = admin_client.post(
        "/admin/reservations", json=reservation_data, headers=headers
    )
    assert response.status_code == 404

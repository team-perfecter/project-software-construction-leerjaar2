from datetime import datetime, timedelta
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


# Tests voor GET /reservations/vehicle/{vehicle_id}
def test_get_reservations_by_vehicle_success(client_with_token):
    client, headers = client_with_token("user")
    vehicle_id = 1
    response = client.get(f"/reservations/vehicle/{vehicle_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_reservations_by_vehicle_unauthorized(client):
    vehicle_id = 1
    response = client.get(f"/reservations/vehicle/{vehicle_id}")
    assert response.status_code == 401


def test_get_reservations_by_vehicle_not_found(client_with_token):
    client, headers = client_with_token("user")
    vehicle_id = 99999
    response = client.get(f"/reservations/vehicle/{vehicle_id}", headers=headers)
    assert response.status_code == 404


def test_get_reservations_by_vehicle_wrong_owner(client_with_token):
    client, headers = client_with_token("user")
    # Assuming vehicle 2 belongs to another user
    vehicle_id = 2
    response = client.get(f"/reservations/vehicle/{vehicle_id}", headers=headers)
    assert response.status_code == 403


def test_get_reservations_by_vehicle_invalid_id(client_with_token):
    client, headers = client_with_token("user")
    response = client.get("/reservations/vehicle/invalid_id", headers=headers)
    assert response.status_code == 422


def test_get_reservations_by_vehicle_empty_list(client_with_token):
    client, headers = client_with_token("user")
    # Create a new vehicle without reservations
    vehicle_response = client.post(
        "/vehicles/create",
        json={
            "license_plate": "TEST123",
            "make": "Test",
            "model": "Car",
            "color": "Red",
            "year": 2024,
        },
        headers=headers,
    )

    if vehicle_response.status_code == 201:
        vehicle_id = vehicle_response.json().get("id")
        response = client.get(f"/reservations/vehicle/{vehicle_id}", headers=headers)
        assert response.status_code == 200
        assert response.json() == []


# Tests voor GET /reservations/{reservation_id} (indien geïmplementeerd)
def test_get_reservation_by_id_success(client_with_token):
    client, headers = client_with_token("user")

    # First create a reservation
    reservation_data = {
        "vehicle_id": 1,
        "parking_lot_id": 1,
        "start_date": "2025-12-10T09:00:00",
        "end_date": "2025-12-10T18:00:00",
    }
    create_response = client.post(
        "/reservations/create", json=reservation_data, headers=headers
    )

    if create_response.status_code in [200, 201]:
        reservation_id = create_response.json().get("reservation_id")
        response = client.get(f"/reservations/{reservation_id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == reservation_id


def test_get_reservation_by_id_not_found(client_with_token):
    client, headers = client_with_token("user")
    response = client.get("/reservations/99999", headers=headers)
    assert response.status_code == 404


def test_get_reservation_by_id_unauthorized(client):
    response = client.get("/reservations/1")
    assert response.status_code == 401


def test_get_reservation_by_id_wrong_owner(client_with_token):
    client, headers = client_with_token("user")
    # Assuming reservation 2 belongs to another user
    response = client.get("/reservations/2", headers=headers)
    assert response.status_code == 403


def test_get_reservation_by_id_invalid_id(client_with_token):
    client, headers = client_with_token("user")
    response = client.get("/reservations/invalid_id", headers=headers)
    assert response.status_code == 422


# Tests voor edge cases
def test_get_reservations_negative_vehicle_id(client_with_token):
    client, headers = client_with_token("user")
    response = client.get("/reservations/vehicle/-1", headers=headers)
    assert response.status_code in [404, 422]


def test_get_reservation_negative_id(client_with_token):
    client, headers = client_with_token("user")
    response = client.get("/reservations/-1", headers=headers)
    assert response.status_code in [404, 422]


@patch(
    "api.models.reservation_model.Reservation_model.get_reservation_by_vehicle",
    return_value=None,
)
def test_get_reservations_by_vehicle_server_error(mock_get, client_with_token):
    client, headers = client_with_token("user")
    response = client.get("/reservations/vehicle/1", headers=headers)
    assert response.status_code == 500


@patch(
    "api.models.reservation_model.Reservation_model.get_reservation_by_id",
    return_value=None,
)
def test_get_reservation_by_id_server_error(mock_get, client_with_token):
    client, headers = client_with_token("user")
    response = client.get("/reservations/1", headers=headers)
    assert response.status_code == 500

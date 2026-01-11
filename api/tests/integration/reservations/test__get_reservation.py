import pytest
from datetime import datetime, timedelta
from api.tests.conftest import get_last_vid, get_last_pid


# region GET /reservations/vehicle/{vehicle_id}
def test_get_reservations_by_vehicle_success(client_with_token):
    """Test successfully retrieving reservations for a vehicle"""
    client, headers = client_with_token("user")
    vehicle_id = get_last_vid(client_with_token)
    parking_lot_id = get_last_pid(client)

    # Create a reservation first
    reservation_data = {
        "vehicle_id": vehicle_id,
        "parking_lot_id": parking_lot_id,
        "start_date": (datetime.now() + timedelta(hours=1)).isoformat(),
        "end_date": (datetime.now() + timedelta(hours=3)).isoformat(),
    }
    client.post("/reservations/create", json=reservation_data, headers=headers)

    # Get reservations for vehicle
    response = client.get(f"/reservations/vehicle/{vehicle_id}", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_get_reservations_by_vehicle_empty(client_with_token):
    """Test retrieving reservations when vehicle has no reservations"""
    client, headers = client_with_token("user")
    vehicle_id = get_last_vid(client_with_token)

    # Get reservations without creating any
    response = client.get(f"/reservations/vehicle/{vehicle_id}", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_get_reservations_vehicle_not_found(client_with_token):
    """Test retrieving reservations for non-existent vehicle"""
    client, headers = client_with_token("user")

    response = client.get("/reservations/vehicle/99999", headers=headers)

    assert response.status_code == 404
    assert "Vehicle not found" in response.json()["detail"]


def test_get_reservations_vehicle_not_owned(client_with_token):
    """Test retrieving reservations for vehicle not owned by user"""
    # Create vehicle as user 1
    user1_client, user1_headers = client_with_token("user")
    vehicle_id = get_last_vid(client_with_token)

    # Try to access as different user
    user2_client, user2_headers = client_with_token("extrauser")
    response = user2_client.get(
        f"/reservations/vehicle/{vehicle_id}", headers=user2_headers
    )

    assert response.status_code == 403
    assert (
        "This vehicle does not belong to the logged in user"
        in response.json()["detail"]
    )


def test_get_reservations_no_authentication(client):
    """Test retrieving reservations without authentication"""
    response = client.get("/reservations/vehicle/1")

    assert response.status_code == 401


def test_get_reservations_invalid_vehicle_id(client_with_token):
    """Test retrieving reservations with invalid vehicle ID format"""
    client, headers = client_with_token("user")

    response = client.get("/reservations/vehicle/invalid", headers=headers)

    assert response.status_code == 422


# endregion

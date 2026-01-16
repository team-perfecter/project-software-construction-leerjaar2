import pytest
from datetime import datetime, timedelta
from api.tests.conftest import get_last_vid, get_last_pid


def test_get_reservations_by_vehicle_success(client_with_token):
    """Test successfully retrieving reservations for a vehicle"""
    client, headers = client_with_token("superadmin")
    vehicle_id = get_last_vid(client_with_token)

    # First check if there are already reservations for this vehicle
    response = client.get(f"/reservations/vehicle/{vehicle_id}", headers=headers)

    # If no reservations exist, create one
    if response.status_code != 200 or not response.json():
        parking_lot_id = get_last_pid(client)
        reservation_data = {
            "vehicle_id": vehicle_id,
            "parking_lot_id": parking_lot_id,
            "start_time": (datetime.now() + timedelta(days=60)).isoformat(),
            "end_time": (datetime.now() + timedelta(days=60, hours=2)).isoformat(),
        }
        create_response = client.post(
            "/reservations/create", json=reservation_data, headers=headers
        )
        assert create_response.status_code in [
            200,
            201,
        ], f"Failed to create reservation: {create_response.json()}"

        # Fetch reservations again
        response = client.get(f"/reservations/vehicle/{vehicle_id}", headers=headers)

    assert response.status_code == 200
    reservations = response.json()
    assert isinstance(reservations, list)
    assert len(reservations) > 0


def test_get_reservations_by_vehicle_empty(client_with_token):
    """Test retrieving reservations when vehicle has no reservations"""
    client, headers = client_with_token("superadmin")

    # Create a new vehicle to ensure it has no reservations
    vehicle_data = {
        "license_plate": "NEWEMPTY999",
        "make": "Honda",
        "model": "Civic",
        "color": "Silver",
        "year": 2023,
        "user_id": 1,  # Added user_id field
    }
    create_vehicle_response = client.post(
        "/vehicles/create", json=vehicle_data, headers=headers
    )

    # If creation fails, print error for debugging
    if create_vehicle_response.status_code != 201:
        print(f"Vehicle creation failed: {create_vehicle_response.json()}")

    assert create_vehicle_response.status_code == 201

    # Get the new vehicle's ID by finding it with the unique license plate
    vehicles_response = client.get("/vehicles", headers=headers)
    vehicles = vehicles_response.json()
    new_vehicle = next(
        (v for v in vehicles if v["license_plate"] == "NEWEMPTY999"), None
    )

    if new_vehicle is None:
        # If we can't find the new vehicle, just use the last one
        vehicle_id = vehicles[-1]["id"]
    else:
        vehicle_id = new_vehicle["id"]

    # Get reservations - should be empty for newly created vehicle
    response = client.get(f"/reservations/vehicle/{vehicle_id}", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # New vehicles should have no reservations
    assert len(data) == 0


def test_get_reservations_vehicle_not_found(client_with_token):
    """Test retrieving reservations for non-existent vehicle"""
    client, headers = client_with_token("superadmin")

    response = client.get("/reservations/vehicle/99999", headers=headers)

    assert response.status_code == 404


def test_get_reservations_vehicle_not_owned(client_with_token):
    """Test retrieving reservations for vehicle not owned by user"""
    # Create vehicle as superadmin
    superadmin_client, superadmin_headers = client_with_token("superadmin")
    vehicle_data = {
        "license_plate": "NOTOWNED888",
        "make": "Toyota",
        "model": "Camry",
        "color": "Blue",
        "year": 2022,
        "user_id": 1,  # Added user_id field (superadmin)
    }
    create_response = superadmin_client.post(
        "/vehicles/create", json=vehicle_data, headers=superadmin_headers
    )

    # If creation fails, print error for debugging
    if create_response.status_code != 201:
        print(f"Vehicle creation failed: {create_response.json()}")

    assert create_response.status_code == 201

    # Get the vehicle ID by finding it with the unique license plate
    vehicles_response = superadmin_client.get("/vehicles", headers=superadmin_headers)
    vehicles = vehicles_response.json()
    new_vehicle = next(
        (v for v in vehicles if v["license_plate"] == "NOTOWNED888"), None
    )

    if new_vehicle is None:
        # If we can't find the new vehicle, just use the last one
        vehicle_id = vehicles[-1]["id"]
    else:
        vehicle_id = new_vehicle["id"]

    # Try to get reservations as different user (user role, not superadmin)
    user_client, user_headers = client_with_token("user")
    response = user_client.get(
        f"/reservations/vehicle/{vehicle_id}", headers=user_headers
    )

    assert response.status_code == 403


def test_get_reservations_no_authentication(client):
    """Test retrieving reservations without authentication"""
    response = client.get("/reservations/vehicle/1")

    assert response.status_code == 401


def test_get_reservations_invalid_vehicle_id(client_with_token):
    """Test retrieving reservations with invalid vehicle ID format"""
    client, headers = client_with_token("superadmin")

    response = client.get("/reservations/vehicle/invalid", headers=headers)

    assert response.status_code == 422

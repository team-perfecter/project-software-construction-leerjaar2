import pytest
from api.tests.conftest import get_last_vid


# region GET /sessions/active
def test_get_active_sessions_success(client_with_token):
    """Test successfully retrieving all active sessions"""
    client, headers = client_with_token("user")
    vehicle_id = get_last_vid(client_with_token)

    # Start a session first
    client.post(
        "/parking-lots/1/sessions/start",
        params={"vehicle_id": vehicle_id},
        headers=headers,
    )

    # Get active sessions
    response = client.get("/sessions/active", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert "active_sessions" in data
    assert isinstance(data["active_sessions"], list)
    assert len(data["active_sessions"]) > 0


def test_get_active_sessions_empty(client_with_token):
    """Test retrieving active sessions when none exist"""
    client, headers = client_with_token("user")

    response = client.get("/sessions/active", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert "active_sessions" in data
    assert isinstance(data["active_sessions"], list)


# endregion


# region GET /sessions/vehicle/{vehicle_id}
def test_get_sessions_vehicle_success(client_with_token):
    """Test successfully retrieving sessions for a specific vehicle"""
    client, headers = client_with_token("user")
    vehicle_id = get_last_vid(client_with_token)

    # Start a session
    client.post(
        "/parking-lots/1/sessions/start",
        params={"vehicle_id": vehicle_id},
        headers=headers,
    )

    # Get sessions for vehicle
    response = client.get(f"/sessions/vehicle/{vehicle_id}", headers=headers)

    assert response.status_code == 201
    data = response.json()
    assert "message" in data


def test_get_sessions_vehicle_not_found(client_with_token):
    """Test retrieving sessions for non-existent vehicle"""
    client, headers = client_with_token("user")

    response = client.get("/sessions/vehicle/99999", headers=headers)

    assert response.status_code == 404
    data = response.json()
    assert "error" in data["detail"]
    assert "Vehicle not found" in data["detail"]["error"]


def test_get_sessions_vehicle_not_owned(client_with_token):
    """Test retrieving sessions for vehicle not owned by user"""
    client, headers = client_with_token("user")

    # Create vehicle for another user
    client2, headers2 = client_with_token("extrauser")
    vehicle_data = {
        "user_id": 5,
        "license_plate": "XYZ789",
        "make": "Honda",
        "model": "Civic",
        "color": "Red",
        "year": 2021,
    }
    vehicle_response = client2.post(
        "/vehicles/create", json=vehicle_data, headers=headers2
    )
    vehicle_id = vehicle_response.json()["id"]

    # Try to get sessions for that vehicle with different user
    response = client.get(f"/sessions/vehicle/{vehicle_id}", headers=headers)

    assert response.status_code == 404
    data = response.json()
    assert "Vehicle not found" in data["detail"]["error"]


def test_get_sessions_vehicle_unauthorized(client):
    """Test retrieving sessions without authentication"""
    response = client.get("/sessions/vehicle/1")

    assert response.status_code == 401


def test_get_sessions_vehicle_invalid_id(client_with_token):
    """Test retrieving sessions with invalid vehicle ID format"""
    client, headers = client_with_token("user")

    response = client.get("/sessions/vehicle/invalid", headers=headers)

    assert response.status_code == 422


# endregion

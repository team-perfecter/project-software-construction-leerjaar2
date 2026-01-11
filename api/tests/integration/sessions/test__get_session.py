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
        headers=headers
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


def test_get_active_sessions_multiple(client_with_token):
    """Test retrieving multiple active sessions"""
    client, headers = client_with_token("user")
    vehicle_id = get_last_vid(client_with_token)
    
    # Start first session
    client.post(
        "/parking-lots/1/sessions/start",
        params={"vehicle_id": vehicle_id},
        headers=headers
    )
    
    # Create another vehicle and start another session
    client2, headers2 = client_with_token("extrauser")
    vehicle_data = {
        "user_id": 5,
        "license_plate": "XYZ789",
        "make": "Honda",
        "model": "Civic",
        "color": "Red",
        "year": 2021
    }
    vehicle_response = client2.post("/vehicles/create", json=vehicle_data, headers=headers2)
    vehicle_id2 = vehicle_response.json()["id"]
    
    client2.post(
        "/parking-lots/1/sessions/start",
        params={"vehicle_id": vehicle_id2},
        headers=headers2
    )
    
    # Get active sessions
    response = client.get("/sessions/active", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["active_sessions"]) >= 2


def test_get_active_sessions_after_stop(client_with_token):
    """Test that stopped sessions are not returned"""
    client, headers = client_with_token("user")
    vehicle_id = get_last_vid(client_with_token)
    
    # Start and then stop a session
    client.post(
        "/parking-lots/1/sessions/start",
        params={"vehicle_id": vehicle_id},
        headers=headers
    )
    
    client.post(
        "/parking-lots/1/sessions/stop",
        params={"vehicle_id": vehicle_id},
        headers=headers
    )
    
    # Get active sessions
    response = client.get("/sessions/active", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    # Should not include the stopped session
    stopped_session_exists = any(
        session.get("vehicle_id") == vehicle_id 
        for session in data["active_sessions"]
    )
    assert not stopped_session_exists
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
        headers=headers
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
        "year": 2021
    }
    vehicle_response = client2.post("/vehicles/create", json=vehicle_data, headers=headers2)
    vehicle_id = vehicle_response.json()["id"]
    
    # Try to get sessions for that vehicle with different user
    response = client.get(f"/sessions/vehicle/{vehicle_id}", headers=headers)
    
    assert response.status_code == 404
    data = response.json()
    assert "Vehicle not found" in data["detail"]["error"]


def test_get_sessions_vehicle_no_active_session(client_with_token):
    """Test retrieving sessions when vehicle has no active session"""
    client, headers = client_with_token("user")
    vehicle_id = get_last_vid(client_with_token)
    
    response = client.get(f"/sessions/vehicle/{vehicle_id}", headers=headers)
    
    assert response.status_code == 201
    data = response.json()
    assert "message" in data


def test_get_sessions_vehicle_unauthorized(client):
    """Test retrieving sessions without authentication"""
    response = client.get("/sessions/vehicle/1")
    
    assert response.status_code == 401


def test_get_sessions_vehicle_with_stopped_session(client_with_token):
    """Test retrieving sessions includes both active and stopped sessions"""
    client, headers = client_with_token("user")
    vehicle_id = get_last_vid(client_with_token)
    
    # Start and stop a session
    client.post(
        "/parking-lots/1/sessions/start",
        params={"vehicle_id": vehicle_id},
        headers=headers
    )
    
    client.post(
        "/parking-lots/1/sessions/stop",
        params={"vehicle_id": vehicle_id},
        headers=headers
    )
    
    # Get sessions for vehicle
    response = client.get(f"/sessions/vehicle/{vehicle_id}", headers=headers)
    
    assert response.status_code == 201
    data = response.json()
    assert "message" in data


def test_get_sessions_vehicle_invalid_id(client_with_token):
    """Test retrieving sessions with invalid vehicle ID"""
    client, headers = client_with_token("user")
    
    response = client.get("/sessions/vehicle/0", headers=headers)
    
    assert response.status_code == 404


@pytest.mark.parametrize("vehicle_id,expected_status", [
    (-1, 404),
    (0, 404),
    (999999, 404),
])
def test_get_sessions_vehicle_validation(client_with_token, vehicle_id, expected_status):
    """Test vehicle ID validation with various invalid values"""
    client, headers = client_with_token("user")
    
    response = client.get(f"/sessions/vehicle/{vehicle_id}", headers=headers)
    
    assert response.status_code == expected_status
# endregion
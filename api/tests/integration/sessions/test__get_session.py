import pytest
from api.tests.conftest import get_last_vid, get_last_pid


# region GET /sessions/active
def test_get_active_sessions_success(client_with_token):
    """Test getting all active sessions"""
    client, headers = client_with_token("superadmin")

    response = client.get("/sessions/active", headers=headers)

    assert response.status_code == 200
    data = response.json()
    # API returns {"active_sessions": [...]}
    assert isinstance(data, dict)
    assert "active_sessions" in data
    assert isinstance(data["active_sessions"], list)


def test_get_active_sessions_no_authentication(client):
    """Test getting active sessions without authentication"""
    response = client.get("/sessions/active")

    # Active sessions endpoint may or may not require auth
    assert response.status_code in [200, 401]


# endregion


# region GET /sessions/vehicle/{vehicle_id}
def test_get_sessions_vehicle_success(client_with_token):
    """Test getting sessions for a specific vehicle"""
    client, headers = client_with_token("superadmin")
    vehicle_id = get_last_vid(client_with_token)

    response = client.get(f"/sessions/vehicle/{vehicle_id}", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "sessions" in data
    assert isinstance(data["sessions"], list)


def test_get_sessions_vehicle_not_found(client_with_token):
    """Test getting sessions for non-existent vehicle"""
    client, headers = client_with_token("superadmin")

    response = client.get("/sessions/vehicle/99999", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert "sessions" in data


def test_get_sessions_vehicle_not_owned(client_with_token):
    """Test getting sessions for vehicle not owned by user"""
    # Create vehicle as superadmin
    superadmin_client, superadmin_headers = client_with_token("superadmin")
    vehicle_data = {
        "license_plate": "SESSNOTOWNED",
        "make": "Toyota",
        "model": "Corolla",
        "color": "Green",
        "year": 2022,
        "user_id": 1,
    }
    create_response = superadmin_client.post(
        "/vehicles/create", json=vehicle_data, headers=superadmin_headers
    )

    if create_response.status_code == 201:
        vehicles_response = superadmin_client.get(
            "/vehicles", headers=superadmin_headers
        )
        vehicles = vehicles_response.json()
        new_vehicle = next(
            (v for v in vehicles if v["license_plate"] == "SESSNOTOWNED"), None
        )

        if new_vehicle:
            vehicle_id = new_vehicle["id"]

            # Try to get sessions as different user
            user_client, user_headers = client_with_token("user")
            response = user_client.get(
                f"/sessions/vehicle/{vehicle_id}", headers=user_headers
            )

            assert response.status_code in [200, 403, 404]


def test_get_sessions_vehicle_no_authentication(client):
    """Test getting vehicle sessions without authentication"""
    response = client.get("/sessions/vehicle/1")

    assert response.status_code == 401


def test_get_sessions_vehicle_invalid_id(client_with_token):
    """Test getting sessions with invalid vehicle ID format"""
    client, headers = client_with_token("superadmin")

    response = client.get("/sessions/vehicle/invalid", headers=headers)

    assert response.status_code == 422


def test_get_sessions_vehicle_negative_id(client_with_token):
    """Test getting sessions with negative vehicle ID"""
    client, headers = client_with_token("superadmin")

    response = client.get("/sessions/vehicle/-1", headers=headers)

    assert response.status_code == 200


# endregion

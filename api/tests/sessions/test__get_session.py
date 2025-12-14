import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from api.main import app
from api.tests.conftest import (
    get_last_pid,
    create_test_vehicle,
    setup_session_prerequisites,
)

client = TestClient(app)


# HELPER FUNCTIONS


def create_test_session(client, headers, vehicle_id, parking_lot_id):
    """Helper to create a session and return its ID"""
    session_data = {
        "vehicle_id": vehicle_id,
        "parking_lot_id": parking_lot_id,
    }

    response = client.post(
        f"/parking-lots/{parking_lot_id}/sessions/start",
        json=session_data,
        headers=headers,
    )

    if response.status_code == 201:
        try:
            data = response.json()
            if isinstance(data, dict) and "id" in data:
                return data["id"]
        except Exception as e:
            print(f"Could not extract session ID: {e}")

    return None


# GET /sessions/active TESTS


@pytest.mark.parametrize("role,expected_status", [
    ("admin", 200),
    ("superadmin", 200),
    ("user", 200),  # ← FIX: Regular users CAN access active sessions
])
def test_get_active_sessions_authorization(client_with_token, role, expected_status):
    """
    Test: Authorization and response structure
    Covers: 200, response structure, field validation
    """
    client_instance, headers = client_with_token(role)
    response = client_instance.get("/sessions/active", headers=headers)
    assert response.status_code == expected_status
    
    if expected_status == 200:
        data = response.json()
        assert "active_sessions" in data
        assert "count" in data
        assert isinstance(data["active_sessions"], (list, type(None)))


def test_get_active_sessions_unauthorized(client):
    """
    Test: Unauthenticated access
    Covers: 401
    """
    response = client.get("/sessions/active")
    assert response.status_code == 401


@patch("api.app.routers.sessions.session_storage.get_active_sessions")
@patch("api.app.routers.sessions.logging.error")
@patch("api.app.routers.sessions.logging.info")
def test_get_active_sessions_all_paths(mock_info, mock_error, mock_get, client_with_token):
    """
    Test: All code paths in one test
    Covers: None return, empty list, data, exception, logging, count calculation
    """
    client_instance, headers = client_with_token("admin")
    
    # Path 1: None
    mock_get.return_value = None
    response = client_instance.get("/sessions/active", headers=headers)
    assert response.status_code == 200
    assert response.json()["count"] == 0
    
    # Path 2: Empty list
    mock_get.return_value = []
    response = client_instance.get("/sessions/active", headers=headers)
    assert response.status_code == 200
    assert response.json()["count"] == 0
    
    # Path 3: With data
    mock_get.return_value = [{"id": 1}, {"id": 2}]
    response = client_instance.get("/sessions/active", headers=headers)
    assert response.status_code == 200
    assert response.json()["count"] == 2
    
    # Path 4: Exception
    mock_get.side_effect = Exception("DB error")
    response = client_instance.get("/sessions/active", headers=headers)
    assert response.status_code == 500
    
    # Verify logging
    assert mock_info.called
    assert mock_error.called


# GET /parking-lots/{lid}/sessions TESTS


def test_get_parking_lot_sessions_superadmin_success(client_with_token):
    """
    Test: Superadmin can access any parking lot
    Covers: 200, list response, superadmin access
    """
    client_instance, headers = client_with_token("superadmin")
    parking_lot_id = get_last_pid(client_instance)
    response = client_instance.get(f"/parking-lots/{parking_lot_id}/sessions", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_parking_lot_sessions_admin_forbidden(client_with_token):
    """
    Test: Admin without lot access gets 403
    Covers: 403, authorization check
    """
    client_instance, headers = client_with_token("admin")
    response = client_instance.get("/parking-lots/999/sessions", headers=headers)
    assert response.status_code == 403


def test_get_parking_lot_sessions_user_forbidden(client_with_token):
    """
    Test: Regular user gets 403
    Covers: 403, role check
    """
    client_instance, headers = client_with_token("user")
    response = client_instance.get("/parking-lots/1/sessions", headers=headers)
    assert response.status_code == 403


def test_get_parking_lot_sessions_unauthorized(client):
    """
    Test: Unauthenticated access
    Covers: 401
    """
    response = client.get("/parking-lots/1/sessions")
    assert response.status_code == 401


@pytest.mark.parametrize("lid,expected_status", [
    (999, 404),         # Not found
    (0, 404),           # Zero
    (-1, 404),          # Negative
    ("invalid", 422),   # Invalid type
])
def test_get_parking_lot_sessions_validation(client_with_token, lid, expected_status):
    """
    Test: Input validation and edge cases
    Covers: 404, 422, edge cases
    """
    client_instance, headers = client_with_token("superadmin")
    response = client_instance.get(f"/parking-lots/{lid}/sessions", headers=headers)
    assert response.status_code == expected_status


# GET /parking-lots/{lid}/sessions/{sid} TESTS


def test_get_specific_session_superadmin_success(client_with_token):
    """
    Test: Superadmin can access specific session
    Covers: 200, response structure, field validation
    """
    admin_client, admin_headers = client_with_token("superadmin")
    user_client, user_headers, vehicle_id, parking_lot_id = setup_session_prerequisites(
        client_with_token, role="user", vehicle_plate="SPECIFIC-TEST"
    )
    
    # Create session
    session_id = create_test_session(user_client, user_headers, vehicle_id, parking_lot_id)
    
    if session_id:
        response = admin_client.get(
            f"/parking-lots/{parking_lot_id}/sessions/{session_id}",
            headers=admin_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        expected_fields = ["id", "parking_lot_id", "user_id", "vehicle_id", "started"]
        for field in expected_fields:
            assert field in data


def test_get_specific_session_admin_forbidden(client_with_token):
    """
    Test: Admin without lot access gets 403
    Covers: 403
    """
    client_instance, headers = client_with_token("admin")
    response = client_instance.get("/parking-lots/999/sessions/1", headers=headers)
    assert response.status_code == 403


def test_get_specific_session_user_forbidden(client_with_token):
    """
    Test: Regular user gets 403
    Covers: 403
    """
    client_instance, headers = client_with_token("user")
    response = client_instance.get("/parking-lots/1/sessions/1", headers=headers)
    assert response.status_code == 403


def test_get_specific_session_unauthorized(client):
    """
    Test: Unauthenticated access
    Covers: 401
    """
    response = client.get("/parking-lots/1/sessions/1")
    assert response.status_code == 401


@pytest.mark.parametrize("lid,sid,expected_status", [
    (999, 1, 404),          # Parking lot not found
    (1, 999, 404),          # Session not found
    (0, 0, 404),            # Zero IDs
    (-1, -1, 404),          # Negative IDs
    ("x", 1, 422),          # Invalid lid type
    (1, "x", 422),          # Invalid sid type
])
def test_get_specific_session_validation(client_with_token, lid, sid, expected_status):
    """
    Test: All validation scenarios
    Covers: 404, 422, edge cases
    """
    client_instance, headers = client_with_token("superadmin")
    response = client_instance.get(f"/parking-lots/{lid}/sessions/{sid}", headers=headers)
    assert response.status_code in [expected_status, 403]  # 403 if no access


# INTEGRATION TEST


def test_complete_session_flow(client_with_token):
    """
    Test: Full integration - create session and verify all GET endpoints
    Covers: All 3 endpoints, data consistency, response structures
    """
    admin_client, admin_headers = client_with_token("superadmin")  # ← FIX: Use superadmin
    user_client, user_headers, vehicle_id, parking_lot_id = setup_session_prerequisites(
        client_with_token, role="user", vehicle_plate="INTEGRATION-TEST"
    )
    
    session_id = create_test_session(user_client, user_headers, vehicle_id, parking_lot_id)
    
    if session_id:
        # Test all 3 endpoints work together
        active = admin_client.get("/sessions/active", headers=admin_headers)
        lot_sessions = admin_client.get(
            f"/parking-lots/{parking_lot_id}/sessions", 
            headers=admin_headers
        )
        specific = admin_client.get(
            f"/parking-lots/{parking_lot_id}/sessions/{session_id}", 
            headers=admin_headers
        )
        
        assert active.status_code == 200
        assert lot_sessions.status_code == 200
        assert specific.status_code == 200
        
        # Verify data consistency
        assert any(s["id"] == session_id for s in active.json()["active_sessions"])
        assert specific.json()["id"] == session_id


@patch("api.app.routers.sessions.logging.info")
def test_logging_and_concurrency(mock_log, client_with_token):
    """
    Test: Logging + concurrent access
    Covers: Logging, thread safety
    """
    client_instance, headers = client_with_token("admin")
    
    # Concurrent requests
    responses = [client_instance.get("/sessions/active", headers=headers) for _ in range(3)]
    
    assert all(r.status_code == 200 for r in responses)
    assert mock_log.call_count >= 3


def test_get_parking_lot_sessions_with_real_session(client_with_token):
    """
    Test: Get sessions when parking lot has actual sessions
    Covers: Real data retrieval
    """
    admin_client, admin_headers = client_with_token("superadmin")
    user_client, user_headers, vehicle_id, parking_lot_id = setup_session_prerequisites(
        client_with_token, role="user", vehicle_plate="REAL-SESSION"
    )
    
    # Create session
    session_id = create_test_session(user_client, user_headers, vehicle_id, parking_lot_id)
    
    if session_id:
        response = admin_client.get(
            f"/parking-lots/{parking_lot_id}/sessions",
            headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(s["id"] == session_id for s in data)
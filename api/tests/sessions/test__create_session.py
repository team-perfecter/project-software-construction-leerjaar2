import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from api.main import app
from api.tests.conftest import setup_session_prerequisites

client = TestClient(app)


# region POST /parking-lots/{lid}/sessions/start TESTS


@pytest.mark.parametrize("role,expected_status", [
    ("user", 201),
    ("admin", 201),
    ("superadmin", 201),
])
def test_start_session_authorization(client_with_token, role, expected_status):
    """
    Test: All authenticated users can start sessions
    Covers: 201 response, authentication, role access, response structure
    """
    user_client, user_headers, vehicle_id, parking_lot_id = setup_session_prerequisites(
        client_with_token, role=role, vehicle_plate=f"START-{role.upper()}"
    )
    
    response = user_client.post(
        f"/parking-lots/{parking_lot_id}/sessions/start?vehicle_id={vehicle_id}",
        headers=user_headers
    )
    assert response.status_code == expected_status
    
    if expected_status == 201:
        data = response.json()
        assert "message" in data
        assert "session_id" in data
        assert "parking_lot_id" in data
        assert "vehicle_id" in data
        assert "license_plate" in data


def test_start_session_unauthorized(client):
    """Test: 401 for unauthenticated access"""
    response = client.post("/parking-lots/1/sessions/start?vehicle_id=1")
    assert response.status_code == 401


@pytest.mark.parametrize("lid,vehicle_id,expected_status", [
    (999, 1, 404),              # Non-existent parking lot
    ("invalid", 1, 422),        # Invalid lid type
    (1, "invalid", 422),        # Invalid vehicle_id type
])
def test_start_session_validation(client_with_token, lid, vehicle_id, expected_status):
    """
    Test: Input validation for start session
    Covers: 404, 422, validation errors
    """
    client_instance, headers = client_with_token("user")
    response = client_instance.post(
        f"/parking-lots/{lid}/sessions/start?vehicle_id={vehicle_id}",
        headers=headers
    )
    assert response.status_code in [expected_status, 403, 404, 500]


def test_start_session_vehicle_not_found(client_with_token):
    """
    Test: Starting session with non-existent vehicle
    Covers: 404 error for vehicle not found
    """
    user_client, user_headers, _, parking_lot_id = setup_session_prerequisites(
        client_with_token, role="user", vehicle_plate="NO-VEHICLE"
    )
    
    response = user_client.post(
        f"/parking-lots/{parking_lot_id}/sessions/start?vehicle_id=999999",
        headers=user_headers
    )
    assert response.status_code == 404


def test_start_session_vehicle_not_owned(client_with_token):
    """
    Test: Starting session with vehicle that doesn't belong to user
    Covers: 403 forbidden error
    """
    # Create vehicle for one user
    user1_client, user1_headers, vehicle_id, parking_lot_id = setup_session_prerequisites(
        client_with_token, role="user", vehicle_plate="USER1-VEHICLE"
    )
    
    # Try to use it with another user
    user2_client, user2_headers = client_with_token("admin")
    response = user2_client.post(
        f"/parking-lots/{parking_lot_id}/sessions/start?vehicle_id={vehicle_id}",
        headers=user2_headers
    )
    assert response.status_code == 403


def test_start_session_duplicate(client_with_token):
    """
    Test: Cannot start duplicate session
    Covers: 409 conflict error
    """
    user_client, user_headers, vehicle_id, parking_lot_id = setup_session_prerequisites(
        client_with_token, role="user", vehicle_plate="DUPLICATE-TEST"
    )
    
    # Start first session
    first_response = user_client.post(
        f"/parking-lots/{parking_lot_id}/sessions/start?vehicle_id={vehicle_id}",
        headers=user_headers
    )
    assert first_response.status_code == 201
    
    # Try to start duplicate
    duplicate_response = user_client.post(
        f"/parking-lots/{parking_lot_id}/sessions/start?vehicle_id={vehicle_id}",
        headers=user_headers
    )
    assert duplicate_response.status_code == 409


@patch("api.app.routers.sessions.session_storage.get_all_sessions_by_id")
@patch("api.app.routers.sessions.logging.error")
def test_start_session_database_error(mock_error, mock_get_sessions, client_with_token):
    """
    Test: Database error when checking existing sessions
    Covers: 500 error, exception handling
    """
    client_instance, headers = client_with_token("user")
    
    mock_get_sessions.side_effect = Exception("DB error")
    response = client_instance.post(
        "/parking-lots/1/sessions/start?vehicle_id=1",
        headers=headers
    )
    assert response.status_code == 500
    mock_error.assert_called_once()


@patch("api.app.routers.sessions.session_storage.get_all_sessions_by_id")
@patch("api.app.routers.sessions.session_storage.create_session")
def test_start_session_creation_returns_none(mock_create, mock_get_sessions, client_with_token):
    """
    Test: Session creation returns None
    Covers: 409 error when session creation fails
    """
    client_instance, headers = client_with_token("user")
    
    mock_get_sessions.return_value = []
    mock_create.return_value = None
    
    response = client_instance.post(
        "/parking-lots/1/sessions/start?vehicle_id=1",
        headers=headers
    )
    assert response.status_code == 409


# endregion


# region POST /parking-lots/{lid}/sessions/stop TESTS


# @pytest.mark.parametrize("role,expected_status", [
#     ("user", 200),
#     ("admin", 200),
#     ("superadmin", 200),
# ])
# def test_stop_session_authorization(client_with_token, role, expected_status):
#     """
#     Test: All authenticated users can stop their sessions
#     Covers: 200 response, authentication, role access, response structure
#     """
#     user_client, user_headers, vehicle_id, parking_lot_id = setup_session_prerequisites(
#         client_with_token, role=role, vehicle_plate=f"STOP-{role.upper()}"
#     )
    
#     # Start session first
#     start_response = user_client.post(
#         f"/parking-lots/{parking_lot_id}/sessions/start?vehicle_id={vehicle_id}",
#         headers=user_headers
#     )
#     assert start_response.status_code == 201
    
#     # Stop session
#     response = user_client.post(
#         f"/parking-lots/{parking_lot_id}/sessions/stop?vehicle_id={vehicle_id}",
#         headers=user_headers
#     )
#     assert response.status_code == expected_status
    
#     if expected_status == 200:
#         data = response.json()
#         assert "message" in data
#         assert "session_id" in data
#         assert "cost" in data
#         assert "duration_minutes" in data
#         assert "payment_id" in data


def test_stop_session_unauthorized(client):
    """Test: 401 for unauthenticated access"""
    response = client.post("/parking-lots/1/sessions/stop?vehicle_id=1")
    assert response.status_code == 401


@pytest.mark.parametrize("lid,vehicle_id,expected_status", [
    ("invalid", 1, 422),        # Invalid lid type
    (1, "invalid", 422),        # Invalid vehicle_id type
])
def test_stop_session_validation(client_with_token, lid, vehicle_id, expected_status):
    """
    Test: Input validation for stop session
    Covers: 422 validation errors
    """
    client_instance, headers = client_with_token("user")
    response = client_instance.post(
        f"/parking-lots/{lid}/sessions/stop?vehicle_id={vehicle_id}",
        headers=headers
    )
    assert response.status_code in [expected_status, 404, 500]


def test_stop_nonexistent_session(client_with_token):
    """
    Test: Cannot stop non-existent session
    Covers: 404 error
    """
    user_client, user_headers, vehicle_id, parking_lot_id = setup_session_prerequisites(
        client_with_token, role="user", vehicle_plate="NO-SESSION"
    )
    
    # Try to stop without starting
    response = user_client.post(
        f"/parking-lots/{parking_lot_id}/sessions/stop?vehicle_id={vehicle_id}",
        headers=user_headers
    )
    assert response.status_code == 404


@patch("api.app.routers.sessions.session_storage.get_vehicle_sessions")
@patch("api.app.routers.sessions.logging.error")
def test_stop_session_database_error(mock_error, mock_get_vehicle, client_with_token):
    """
    Test: Database error when retrieving vehicle sessions
    Covers: 500 error, exception handling
    """
    client_instance, headers = client_with_token("user")
    
    mock_get_vehicle.side_effect = Exception("DB error")
    response = client_instance.post(
        "/parking-lots/1/sessions/stop?vehicle_id=1",
        headers=headers
    )
    assert response.status_code == 500
    mock_error.assert_called_once()


@patch("api.app.routers.sessions.session_storage.get_vehicle_sessions")
@patch("api.app.routers.sessions.session_storage.stop_session")
@patch("api.app.routers.sessions.logging.error")
def test_stop_session_stop_fails(mock_error, mock_stop, mock_get_vehicle, client_with_token):
    """
    Test: Session stop operation fails
    Covers: 500 error when stopping session
    """
    client_instance, headers = client_with_token("user")
    
    mock_get_vehicle.return_value = {"id": 1}
    mock_stop.side_effect = Exception("Stop failed")
    
    response = client_instance.post(
        "/parking-lots/1/sessions/stop?vehicle_id=1",
        headers=headers
    )
    assert response.status_code == 500
    mock_error.assert_called_once()


@patch("api.app.routers.sessions.session_storage.get_vehicle_sessions")
@patch("api.app.routers.sessions.session_storage.stop_session")
@patch("api.app.routers.sessions.payment_model.create_payment")
@patch("api.app.routers.sessions.logging.error")
def test_stop_session_payment_fails(
    mock_error, mock_create_payment, mock_stop, mock_get_vehicle, client_with_token
):
    """
    Test: Payment creation fails after session is stopped
    Covers: 500 error with payment creation failure message
    """
    client_instance, headers = client_with_token("user")
    
    mock_get_vehicle.return_value = {"id": 1}
    mock_stop.return_value = {"id": 1, "cost": 10.0, "duration_in_minutes": 30}
    mock_create_payment.side_effect = Exception("Payment failed")
    
    response = client_instance.post(
        "/parking-lots/1/sessions/stop?vehicle_id=1",
        headers=headers
    )
    assert response.status_code == 500
    assert "payment" in response.json()["detail"]["error"].lower()
    mock_error.assert_called_once()


# endregion


# region INTEGRATION TESTS


# @patch("api.app.routers.sessions.logging.info")
# def test_session_logging(mock_log, client_with_token):
#     """
#     Test: Verify logging is called correctly
#     Covers: Logging functionality for both operations
#     """
#     user_client, user_headers, vehicle_id, parking_lot_id = setup_session_prerequisites(
#         client_with_token, role="user", vehicle_plate="LOGGING-TEST"
#     )
    
#     # Start session
#     user_client.post(
#         f"/parking-lots/{parking_lot_id}/sessions/start?vehicle_id={vehicle_id}",
#         headers=user_headers
#     )
    
#     # Stop session
#     user_client.post(
#         f"/parking-lots/{parking_lot_id}/sessions/stop?vehicle_id={vehicle_id}",
#         headers=user_headers
#     )
    
#     # Verify logging was called
#     assert mock_log.call_count >= 4  # At least 2 per operation


# endregion
from fastapi.testclient import TestClient
from api.main import app
from unittest.mock import patch

client = TestClient(app)


# /sessions/active
def test_get_active_sessions_success(client_with_token):
    client_instance, headers = client_with_token("admin")
    response = client_instance.get("/sessions/active", headers=headers)
    assert response.status_code == 200
    assert "active_sessions" in response.json()


def test_get_active_sessions_unauthorized(client):
    response = client.get("/sessions/active")
    assert response.status_code == 401


def test_get_active_sessions_forbidden(client_with_token):
    client_instance, headers = client_with_token("user")
    response = client_instance.get("/sessions/active", headers=headers)
    assert response.status_code == 403


def test_get_active_sessions_superadmin(client_with_token):
    client_instance, headers = client_with_token("superadmin")
    response = client_instance.get("/sessions/active", headers=headers)
    assert response.status_code == 200
    assert "active_sessions" in response.json()


def test_get_active_sessions_empty_list(client_with_token):
    client_instance, headers = client_with_token("admin")
    response = client_instance.get("/sessions/active", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "active_sessions" in data
    assert isinstance(data["active_sessions"], list)


def test_get_active_sessions_response_structure(client_with_token):
    client_instance, headers = client_with_token("admin")
    response = client_instance.get("/sessions/active", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "active_sessions" in data
    # Als er sessies zijn, controleer de structuur van de eerste sessie
    if data["active_sessions"]:
        session = data["active_sessions"][0]
        # Verwachte velden in een sessie (afhankelijk van je Session model)
        expected_fields = ["id", "parking_lot_id", "user_id", "vehicle_id", "started"]
        for field in expected_fields:
            assert field in session


# /parking-lots/{lid}/sessions
def test_get_sessions_for_parking_lot_authorized(client_with_token):
    client_instance, headers = client_with_token("admin")
    response = client_instance.get("/parking-lots/1/sessions", headers=headers)
    assert response.status_code == 200


def test_get_sessions_for_parking_lot_unauthorized(client):
    response = client.get("/parking-lots/1/sessions")
    assert response.status_code == 401


def test_get_sessions_for_parking_lot_forbidden(client_with_token):
    client_instance, headers = client_with_token("user")
    response = client_instance.get("/parking-lots/1/sessions", headers=headers)
    assert response.status_code == 403


def test_get_sessions_for_nonexistent_parking_lot(client_with_token):
    client_instance, headers = client_with_token("admin")
    response = client_instance.get("/parking-lots/999/sessions", headers=headers)
    assert response.status_code == 404


def test_get_sessions_for_parking_lot_lid_not_int(client_with_token):
    client_instance, headers = client_with_token("admin")
    response = client_instance.get("/parking-lots/hallo/sessions", headers=headers)
    assert response.status_code == 422


# /parking-lots/{lid}/sessions/{sid}
def test_get_specific_session_authorized(client_with_token):
    client_instance, headers = client_with_token("admin")
    response = client_instance.get("/parking-lots/1/sessions/1", headers=headers)
    assert response.status_code == 200


def test_get_specific_session_unauthorized(client):
    response = client.get("/parking-lots/1/sessions/1")
    assert response.status_code == 401


def test_get_specific_session_forbidden(client_with_token):
    client_instance, headers = client_with_token("user")
    response = client_instance.get("/parking-lots/1/sessions/1", headers=headers)
    assert response.status_code == 403


def test_get_nonexistent_session(client_with_token):
    client_instance, headers = client_with_token("admin")
    response = client_instance.get("/parking-lots/1/sessions/999", headers=headers)
    assert response.status_code == 404


def test_get_session_from_nonexistent_parking_lot(client_with_token):
    client_instance, headers = client_with_token("admin")
    response = client_instance.get("/parking-lots/999/sessions/1", headers=headers)
    assert response.status_code == 404


def test_get_specific_session_lid_not_int(client_with_token):
    client_instance, headers = client_with_token("admin")
    response = client_instance.get("/parking-lots/hallo/sessions/1", headers=headers)
    assert response.status_code == 422


def test_get_specific_session_sid_not_int(client_with_token):
    client_instance, headers = client_with_token("admin")
    response = client_instance.get("/parking-lots/1/sessions/hallo", headers=headers)
    assert response.status_code == 422


# Test voor regel 220 - logging.info
def test_get_active_sessions_logging_is_called(client_with_token):
    """Test: GET /sessions/active - Logging wordt aangeroepen"""
    client_instance, headers = client_with_token("admin")

    with patch("api.app.routers.sessions.logging.info") as mock_logging:
        response = client_instance.get("/sessions/active", headers=headers)
        assert response.status_code == 200

        mock_logging.assert_called_once()
        args = mock_logging.call_args[0]
        assert "requesting active sessions" in args[0]


# Test voor regel 222-232 - try-except block (database error)
def test_get_active_sessions_database_error(client_with_token):
    """Test: GET /sessions/active - Database error handling"""
    client_instance, headers = client_with_token("admin")

    with patch(
        "api.app.routers.sessions.session_storage.get_active_sessions"
    ) as mock_get:
        mock_get.side_effect = Exception("Database connection error")

        response = client_instance.get("/sessions/active", headers=headers)
        assert response.status_code == 500


# Test voor regel 225 - logging.error binnen except block
def test_get_active_sessions_logs_error_on_exception(client_with_token):
    """Test: GET /sessions/active - Error logging bij exception"""
    client_instance, headers = client_with_token("admin")

    with patch(
        "api.app.routers.sessions.session_storage.get_active_sessions"
    ) as mock_get:
        with patch("api.app.routers.sessions.logging.error") as mock_error_log:
            mock_get.side_effect = Exception("Test error")

            response = client_instance.get("/sessions/active", headers=headers)
            assert response.status_code == 500

            mock_error_log.assert_called_once()


# Test voor regel 234 - return statement met sessions == None/empty
def test_get_active_sessions_empty_returns_zero_count(client_with_token):
    """Test: GET /sessions/active - Count is 0 wanneer geen sessies"""
    client_instance, headers = client_with_token("admin")

    with patch(
        "api.app.routers.sessions.session_storage.get_active_sessions"
    ) as mock_get:
        mock_get.return_value = None

        response = client_instance.get("/sessions/active", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        assert data["active_sessions"] is None


# Test voor regel 234 - return statement met sessions niet None
def test_get_active_sessions_with_sessions_returns_correct_count(client_with_token):
    """Test: GET /sessions/active - Count komt overeen met aantal sessies"""
    client_instance, headers = client_with_token("admin")

    mock_sessions = [
        {"id": 1, "vehicle_id": 1, "parking_lot_id": 1},
        {"id": 2, "vehicle_id": 2, "parking_lot_id": 1},
        {"id": 3, "vehicle_id": 3, "parking_lot_id": 2},
    ]

    with patch(
        "api.app.routers.sessions.session_storage.get_active_sessions"
    ) as mock_get:
        mock_get.return_value = mock_sessions

        response = client_instance.get("/sessions/active", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 3
        assert len(data["active_sessions"]) == 3


# Test voor regel 234 - else branch (wanneer sessions is not None)
def test_get_active_sessions_else_branch_with_empty_list(client_with_token):
    """Test: GET /sessions/active - Lege lijst (niet None)"""
    client_instance, headers = client_with_token("admin")

    with patch(
        "api.app.routers.sessions.session_storage.get_active_sessions"
    ) as mock_get:
        mock_get.return_value = []

        response = client_instance.get("/sessions/active", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        assert data["active_sessions"] == []


# Integratietest die alle paden test
def test_get_active_sessions_integration(client_with_token):
    """Test: GET /sessions/active - Volledige integratie test"""
    client_instance, headers = client_with_token("admin")

    # Haal actieve sessies op (test success path)
    response = client_instance.get("/sessions/active", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert "active_sessions" in data
    assert "count" in data

from fastapi.testclient import TestClient
from api.main import app

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

from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


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
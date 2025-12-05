from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


# /parking-lots/{lid}/sessions/start
def test_start_session_authorized(client_with_token):
    client_instance, headers = client_with_token("user")
    vehicle = {"vehicle_id": 1}
    response = client_instance.post("/parking-lots/1/sessions/start", headers=headers, json=vehicle)
    assert response.status_code == 200


def test_start_session_unauthorized(client):
    vehicle = {"vehicle_id": 1}
    response = client.post("/parking-lots/1/sessions/start", json=vehicle)
    assert response.status_code == 401


def test_start_session_missing_vehicle_id(client_with_token):
    client_instance, headers = client_with_token("user")
    vehicle = {}
    response = client_instance.post("/parking-lots/1/sessions/start", headers=headers, json=vehicle)
    assert response.status_code == 422


def test_start_session_nonexistent_parking_lot(client_with_token):
    client_instance, headers = client_with_token("user")
    vehicle = {"vehicle_id": 1}
    response = client_instance.post("/parking-lots/999/sessions/start", headers=headers, json=vehicle)
    assert response.status_code == 404


def test_start_session_invalid_vehicle_id(client_with_token):
    client_instance, headers = client_with_token("user")
    vehicle = {"vehicle_id": 999}
    response = client_instance.post("/parking-lots/1/sessions/start", headers=headers, json=vehicle)
    assert response.status_code == 404


def test_start_session_lid_not_int(client_with_token):
    client_instance, headers = client_with_token("user")
    vehicle = {"vehicle_id": 1}
    response = client_instance.post("/parking-lots/hallo/sessions/start", headers=headers, json=vehicle)
    assert response.status_code == 422


# /parking-lots/{lid}/sessions/stop
def test_stop_session_authorized(client_with_token):
    client_instance, headers = client_with_token("user")
    session = {"session_id": 1}
    response = client_instance.post("/parking-lots/1/sessions/stop", headers=headers, json=session)
    assert response.status_code == 200


def test_stop_session_unauthorized(client):
    session = {"session_id": 1}
    response = client.post("/parking-lots/1/sessions/stop", json=session)
    assert response.status_code == 401


def test_stop_session_missing_session_id(client_with_token):
    client_instance, headers = client_with_token("user")
    session = {}
    response = client_instance.post("/parking-lots/1/sessions/stop", headers=headers, json=session)
    assert response.status_code == 422


def test_stop_nonexistent_session(client_with_token):
    client_instance, headers = client_with_token("user")
    session = {"session_id": 999}
    response = client_instance.post("/parking-lots/1/sessions/stop", headers=headers, json=session)
    assert response.status_code == 404


def test_stop_session_from_nonexistent_parking_lot(client_with_token):
    client_instance, headers = client_with_token("user")
    session = {"session_id": 1}
    response = client_instance.post("/parking-lots/999/sessions/stop", headers=headers, json=session)
    assert response.status_code == 404


def test_stop_session_lid_not_int(client_with_token):
    client_instance, headers = client_with_token("user")
    session = {"session_id": 1}
    response = client_instance.post("/parking-lots/hallo/sessions/stop", headers=headers, json=session)
    assert response.status_code == 422


def test_stop_session_invalid_session_id(client_with_token):
    client_instance, headers = client_with_token("user")
    session = {"session_id": "invalid"}
    response = client_instance.post("/parking-lots/1/sessions/stop", headers=headers, json=session)
    assert response.status_code == 422
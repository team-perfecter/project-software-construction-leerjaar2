from unittest.mock import patch
from datetime import datetime, timedelta
import jwt
import pytest
from fastapi.testclient import TestClient
from ../../app import app

'''
A function that creates a new authorization token so a user can be verified
'''
def create_test_token(username: str):
    expire = datetime.utcnow() + timedelta(minutes=30)
    token = jwt.encode({"sub": username, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)
    return token

valid_token = create_test_token("alice")
valid_headers = {"Authorization": f"Bearer {valid_token}"}
invalid_headers = {"Authorization": "Bearer invalid"}

'''
Fake data
'''
def fake_start_session(lid: int, vehicle_id: int):
    if lid not in [101, 202]:
        return {"error": "Parking lot not found"}
    if not vehicle_id:
        return {"error": "Missing vehicle ID"}
    return {
        "session_id": 1,
        "lot_id": lid,
        "vehicle_id": vehicle_id,
        "start_time": "2025-12-01T10:00:00Z",
        "status": "active"
    }

def fake_stop_session(lid: int, sid: int):
    if lid not in [101, 202]:
        return {"error": "Parking lot not found"}
    if sid != 1:
        return {"error": "Session not found"}
    return {
        "session_id": sid,
        "lot_id": lid,
        "end_time": "2025-12-01T12:00:00Z",
        "status": "stopped"
    }

'''
Start een sessie op een parkeerplaats (ingelogd).
'''
def test_start_session_authorized():
    with patch("app.routers.parking.db_start_session", side_effect=fake_start_session):
        payload = {"vehicle_id": 55}
        response = client.post("/parking-lots/101/sessions/start", headers=valid_headers, json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["lot_id"] == 101
        assert data["vehicle_id"] == 55
        assert data["status"] == "active"

'''
Start een sessie zonder geldige token.
'''
def test_start_session_not_authorized():
    payload = {"vehicle_id": 55}
    response = client.post("/parking-lots/101/sessions/start", headers=invalid_headers, json=payload)
    assert response.status_code == 401

'''
Probeer een sessie te starten zonder voertuig-ID.
'''
def test_start_session_missing_vehicle_id():
    with patch("app.routers.parking.db_start_session", side_effect=fake_start_session):
        payload = {}
        response = client.post("/parking-lots/101/sessions/start", headers=valid_headers, json=payload)
        assert response.status_code in [400, 422]
        data = response.json()
        assert "error" in data or "detail" in data

'''
Probeer een sessie te starten op een niet-bestaande parkeerplaats.
'''
def test_start_session_nonexistent_lot():
    with patch("app.routers.parking.db_start_session", side_effect=fake_start_session):
        payload = {"vehicle_id": 55}
        response = client.post("/parking-lots/999/sessions/start", headers=valid_headers, json=payload)
        data = response.json()
        assert response.status_code == 404 or "error" in data

'''
Stop een sessie op een parkeerplaats (ingelogd).
'''
def test_stop_session_authorized():
    with patch("app.routers.parking.db_stop_session", side_effect=fake_stop_session):
        response = client.post("/parking-lots/101/sessions/stop", headers=valid_headers, json={"session_id": 1})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "stopped"
        assert "end_time" in data

'''
Stop een sessie zonder geldige token.
'''
def test_stop_session_not_authorized():
    response = client.post("/parking-lots/101/sessions/stop", headers=invalid_headers, json={"session_id": 1})
    assert response.status_code == 401

'''
Stop een sessie die niet bestaat.
'''
def test_stop_nonexistent_session():
    with patch("app.routers.parking.db_stop_session", side_effect=fake_stop_session):
        response = client.post("/parking-lots/101/sessions/stop", headers=valid_headers, json={"session_id": 99})
        data = response.json()
        assert response.status_code == 404 or "error" in data
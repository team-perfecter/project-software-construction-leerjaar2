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
def get_fake_sessions_for_lot(lid: int):
    sessions = [
        {"id": 1, "lot_id": 101, "vehicle_id": 20, "start_time": "2025-12-01T10:00:00Z", "end_time": "2025-12-01T12:00:00Z"},
        {"id": 2, "lot_id": 101, "vehicle_id": 21, "start_time": "2025-12-01T13:00:00Z", "end_time": "2025-12-01T15:00:00Z"},
        {"id": 3, "lot_id": 202, "vehicle_id": 22, "start_time": "2025-12-02T09:00:00Z", "end_time": "2025-12-02T11:00:00Z"}
    ]
    return [s for s in sessions if s["lot_id"] == lid]

def get_fake_session(lid: int, sid: int):
    sessions = get_fake_sessions_for_lot(lid)
    for s in sessions:
        if s["id"] == sid:
            return s
    return None

'''
Haal alle sessions voor een parkeerplaats op (ingelogd).
'''
def test_get_sessions_for_parking_lot_authorized():
    with patch("app.routers.parking.db_get_sessions_for_lot", side_effect=get_fake_sessions_for_lot):
        response = client.get("/parking-lots/101/sessions", headers=valid_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        assert all(session["lot_id"] == 101 for session in data)

'''
Haal alle sessions voor een parkeerplaats op zonder geldige token.
'''
def test_get_sessions_for_parking_lot_not_authorized():
    response = client.get("/parking-lots/101/sessions", headers=invalid_headers)
    assert response.status_code == 401

'''
Haal alle sessions op voor een parkeerplaats die niet bestaat.
'''
def test_get_sessions_for_nonexistent_parking_lot():
    with patch("app.routers.parking.db_get_sessions_for_lot", side_effect=get_fake_sessions_for_lot):
        response = client.get("/parking-lots/999/sessions", headers=valid_headers)
        data = response.json()
        assert response.status_code == 404 or data == []

'''
Haal specifieke session op (ingelogd).
'''
def test_get_specific_session_authorized():
    with patch("app.routers.parking.db_get_session", side_effect=get_fake_session):
        response = client.get("/parking-lots/101/sessions/1", headers=valid_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["lot_id"] == 101

'''
Haal specifieke session op zonder geldige token.
'''
def test_get_specific_session_not_authorized():
    response = client.get("/parking-lots/101/sessions/1", headers=invalid_headers)
    assert response.status_code == 401

'''
Haal specifieke session op die niet bestaat.
'''
def test_get_nonexistent_session():
    with patch("app.routers.parking.db_get_session", side_effect=get_fake_session):
        response = client.get("/parking-lots/101/sessions/99", headers=valid_headers)
        assert response.status_code == 404
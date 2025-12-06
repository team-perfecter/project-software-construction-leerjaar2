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
def fake_delete_session(lid: int, sid: int):
    if lid not in [101, 202]:
        return {"error": "Parking lot not found"}
    if sid != 1:
        return {"error": "Session not found"}
    return {"message": f"Session {sid} deleted successfully"}

'''
Verwijder een sessie (ingelogd).
'''
def test_delete_session_authorized():
    with patch("app.routers.parking.db_delete_session", side_effect=fake_delete_session):
        response = client.delete("/parking-lots/101/sessions/1", headers=valid_headers)
        assert response.status_code == 200
        data = response.json()
        assert "deleted" in data["message"].lower()

'''
Probeer een sessie te verwijderen zonder geldige token.
'''
def test_delete_session_not_authorized():
    response = client.delete("/parking-lots/101/sessions/1", headers=invalid_headers)
    assert response.status_code == 401

'''
Probeer een niet-bestaande sessie te verwijderen.
'''
def test_delete_nonexistent_session():
    with patch("app.routers.parking.db_delete_session", side_effect=fake_delete_session):
        response = client.delete("/parking-lots/101/sessions/99", headers=valid_headers)
        data = response.json()
        assert response.status_code == 404 or "error" in data

'''
Probeer een sessie te verwijderen op een niet-bestaande parkeerplaats.
'''
def test_delete_session_from_nonexistent_lot():
    with patch("app.routers.parking.db_delete_session", side_effect=fake_delete_session):
        response = client.delete("/parking-lots/999/sessions/1", headers=valid_headers)
        data = response.json()
        assert response.status_code == 404 or "error" in data
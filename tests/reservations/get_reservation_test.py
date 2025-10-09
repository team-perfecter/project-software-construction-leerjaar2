from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from ../../app import app

'''
reservations will be in a seperate class. the input of this class will be the authorization token of the user.
each endpoint will check if the token is valid. if not valid, return 401
the validity of a token is checked in the get_user(token: str = Depends(oauth2_scheme)) function.
get_reservation(rid: int) returns the reservation with the given reservation id. this happens with the function db_get_reservation(id; int)
get_reservation returns the followinig:
{"reservation": db_get_reservation(id: int)}

'''

client = TestClient(app)

'''
A function that creates a new authorization token so a user can be verified
'''
def create_test_token(username: str):
    expire = datetime.utcnow() + timedelta(minutes=30)
    token = jwt.encode({"sub": username, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)
    return token

token = create_test_token("alice")
valid_headers = {"Authorization": f"Bearer {token}"}
invalid_header = {"Authorization": "Bearer invalid"}

def get_fake_reservation(rid: int):
    return [{
        "id": "1",
        "user_id": "1",
        "parking_lot_id": "217",
        "vehicle_id": "471",
        "start_time": "2025-12-03T11:00:00Z",
        "end_time": "2025-12-03T14:00:00Z",
        "status": "confirmed",
        "created_at": "2025-12-01T11:00:00Z",
        "cost": 7.5
    },
    {
        "id": "2",
        "user_id": "2",
        "parking_lot_id": "165",
        "vehicle_id": "2385",
        "start_time": "2025-12-01T17:30:00Z",
        "end_time": "2025-12-01T20:30:00Z",
        "status": "confirmed",
        "created_at": "2025-11-04T17:30:00Z",
        "cost": 4.2
    }][rid]

'''
Test if a reservation is properly received.
'''
def test_get_reservation_when_authorized():
    response = client.get("/reservations/", headers=valid_headers)
    with patch("db_get_reservation", side_effect=get_fake_reservation):
        res = get_reservation(0)
        assert res["id"] == get_fake_reservation
        assert response.status_code == 200

'''
Test what will happen when a reservation does not exist.
'''
def test_get_empty_reservation():
    response = client.get("/reservations", headers=valid_headers)
    with patch("db_get_reservation", side_effect=get_fake_reservation):
        res = get_reservation(2)
        assert res["id"] == None
        assert response.status_code == 404

'''
Test what will happen when a user tries to get a reservation when not authorized
'''
def test_get_reservation_not_authorized():
    response = client.get("/reservations", headers=invalid_header)
    with patch("db_get_reservation", side_effect=get_fake_reservation):
        res = get_reservation(0)
        assert res["id"] == None
        assert response.status_code == 401
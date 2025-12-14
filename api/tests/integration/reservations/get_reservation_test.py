from dataclasses import dataclass
from datetime import date
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
def create_test_token(username: str) -> str:
    expire: date = datetime.utcnow() + timedelta(minutes=30)
    token: str = jwt.encode({"sub": username, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)
    return token

token: str = create_test_token("test")
valid_headers: dict[str, str] = {"Authorization": f"Bearer {token}"}
invalid_header: dict[str, str] = {"Authorization": "Bearer invalid"}

@dataclass
class Reservation:
    id: int
    user_id: int
    parking_lot_id: int
    vehicle_id: int
    start_time: str
    end_time: str
    status: str
    created_at: str
    cost: float


def get_fake_reservation(rid: int) -> Reservation:
    return [        
        Reservation(
            1, 
            1, 
            217, 
            471, 
            '2025-12-03T11:00:00Z', 
            '2025-12-03T14:00:00Z', 
            'confirmed', 
            '2025-12-01T11:00:00Z', 
            7.5
        ),
        Reservation(
            2, 
            2, 
            165, 
            2385, 
            '2025-12-01T17:30:00Z', 
            '2025-12-01T20:30:00Z', 
            'confirmed', 
            '2025-11-04T17:30:00Z', 
            4.2
        )
    ][rid]

'''
Test if a reservation is properly received.
'''
@patch("path.to.function.db_get_reservation", side_effect=get_fake_reservation)
def test_get_reservation_when_authorized() -> None:
    response = client.get("/reservations/0", headers=valid_headers)
    data = response.json()
    assert response.status_code == 200
    assert data.id == 1
    

'''
Test what will happen when a reservation does not exist.
'''
@patch("path.to.function.db_get_reservation", side_effect=get_fake_reservation)
def test_get_empty_reservation() -> None:
    response = client.get("/reservations/2", headers=valid_headers)
    assert response.status_code == 404

'''
Test what will happen when a user tries to get a reservation when not authorized
'''
@patch("path.to.function.db_get_reservation", side_effect=get_fake_reservation)
def test_get_reservation_not_authorized() -> None:
    response = client.get("/reservations/1", headers=invalid_header)
    assert response.status_code == 401
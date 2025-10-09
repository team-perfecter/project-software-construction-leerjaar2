from dataclasses import asdict, dataclass
from datetime import date
import json
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from ../../app import app

'''
reservations will be in a seperate class. the input of this class will be the authorization token of the user.
each endpoint will check if the token is valid. if not valid, return 401
the validity of a token is checked in the get_user(token: str = Depends(oauth2_scheme)) function.
db_post_reservation() is a function that posts a function to the database. 
retrieve all reservations where the parking lot or vehicle is the same as the reservation a user is trying to create
check if there is any overlap between either the parking lot or the vehicle
return an error if there is any overlap

'''

client = TestClient(app)

@dataclass
class Reservation:
    parking_lot_id: int
    payment_id: int
    user_id: int
    license_plate: str
    started: str

@dataclass
class Parking_location:
    id: int
    name: str
    location: str
    adress: str
    capacity: int
    reserved: int
    tariff: float
    daytariff: float
    created_at: date
    lat: float
    lng: float

@dataclass
class Vehicle:
    id: int
    user_id: int
    license_plate: str
    make: str
    model: str
    color: str
    year: int
    created_at: date

def get_fake_parking_location(id: int) -> Parking_location:
    return [
        {
            1, 
            "Bedrijventerrein Almere Parkeergarage", 
            "Industrial Zone", 
            "Schanssingel 337, 2421 BS Almere", 
            335, 
            77, 
            1.9, 
            11, 
            "2020-03-25", 
            52.3133, 
            5.2234
        }, 
        {
            1, 
            "Bedrijventerrein Almere Parkeergarage", 
            "Industrial Zone", 
            "Schanssingel 337, 2421 BS Almere", 
            335, 
            355, 
            1.9, 
            11, 
            "2020-03-25", 
            52.3133, 
            5.2234
        }
        ][id]

def get_fake_vehicle(id: int) -> Vehicle:
    return [
        {
            0,
            0,
            "",
            "",
            "",
            "",
            2005,
            "2020-03-25"
        }, 
        {
            1,
            0,
            "",
            "",
            "",
            "",
            2005,
            "2020-03-25"
        }
        ][id]
    

reservations: list[Reservation] = []

def fake_post_reservation(reservation: Reservation) -> None:
    reservations.append(reservation)

def get_fake_reservations(rid: int)-> Reservation:
    result: Reservation = None
    for res in reservations:
        if res["id"] == rid:
            result = res
    return result

def create_test_token(username: str) -> str:
    expire: date = datetime.utcnow() + timedelta(minutes=30)
    token: str = jwt.encode({"sub": username, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)
    return token

token: str = create_test_token("test")
valid_header: dict[str, str] = {"Authorization": f"Bearer {token}"}
invalid_header: dict[str, str] = {"Authorization": "Bearer invalid"}

'''
Test creating a new reservation when a user is authorized.
'''
@patch("path.to.function.db_post_reservation", side_effect=fake_post_reservation)
@patch("path.to.function.db_get_parking_locations", side_effect=get_fake_parking_location)
@patch("path.to.function.db_get_vehicle", side_effect=get_fake_vehicle)
def test_create_reservation_when_authorized() -> None:
    data: Reservation = Reservation(0, 1, 1, "aaaaa", str(date.today()))
    response = client.post("/reservations", headers=valid_header, json=asdict(data))
    assert response.status_code == 200
    assert len(reservations) == 1
    assert reservations[0].parking_lot_id == 1
    reservations.clear()


'''
Test creating a new reservation when a user is not authorized.
'''
@patch("path.to.function.db_post_reservation", side_effect=fake_post_reservation)
@patch("path.to.function.db_get_parking_locations", side_effect=get_fake_parking_location)
@patch("path.to.function.db_get_vehicle", side_effect=get_fake_vehicle)
def test_create_reservation_when_not_authorized() -> None:
    data: Reservation = Reservation(1, 1, 1, "aaaa", str(date.today()))
    response = client.post("/reservations", headers=invalid_header, json=asdict(data))
    assert response.status_code == 401
    reservations.clear()


'''
Test creating a new reservation when a user has not filled in all data
'''
@patch("path.to.function.db_post_reservation", side_effect=fake_post_reservation)
@patch("path.to.function.db_get_parking_locations", side_effect=get_fake_parking_location)
@patch("path.to.function.db_get_vehicle", side_effect=get_fake_vehicle)
def test_create_reservation_when_date_incomplete() -> None:
    response = client.post("/reservations", headers=valid_header, json={"parking_lot_id": 11})
    assert response.status_code == 422
    assert reservations.len() == 0
    reservations.clear()

'''
Test creating a new reservation when a parking location does not exist
'''
@patch("path.to.function.db_post_reservation", side_effect=fake_post_reservation)
@patch("path.to.function.db_get_parking_locations", side_effect=get_fake_parking_location)
@patch("path.to.function.db_get_vehicle", side_effect=get_fake_vehicle)
def test_create_reservation_when_date_incomplete() -> None:
    data: Reservation = Reservation(0, 1, 1, "aaaaa", str(date.today()))
    response = client.post("/reservations", headers=valid_header, json=asdict(data))
    assert response.status_code == 404
    assert reservations.len() == 0
    reservations.clear()

'''
Test creating a new reservation when a parking location is already full
'''
@patch("path.to.function.db_post_reservation", side_effect=fake_post_reservation)
@patch("path.to.function.db_get_parking_locations", side_effect=get_fake_parking_location)
@patch("path.to.function.db_get_vehicle", side_effect=get_fake_vehicle)
def test_create_reservation_when_parking_location_full() -> None:
    data: Reservation = Reservation(1, 1, 1, "aaaaa", str(date.today()))
    response = client.post("/reservations", headers=valid_header, json=asdict(data))
    assert response.status_code == 403
    assert reservations.len() == 0
    reservations.clear()


'''
Test creating a new reservation when a vehicle already has a reservation
'''
@patch("path.to.function.db_post_reservation", side_effect=fake_post_reservation)
@patch("path.to.function.db_get_parking_locations", side_effect=get_fake_parking_location)
@patch("path.to.function.db_get_vehicle", side_effect=get_fake_vehicle)
def test_create_reservation_when_vehicle_has_reservation() -> None:
    data: Reservation = Reservation(1, 1, 1, "aaaaa", str(date.today()))
    fake_post_reservation(data)
    response = client.post("/reservations", headers=valid_header, json=asdict(data))
    assert response.status_code == 403
    assert reservations.len() == 1
    reservations.clear()

'''
Test creating a new reservation when a vehicle is already parked
'''
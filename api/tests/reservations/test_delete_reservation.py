from dataclasses import asdict, dataclass
from datetime import date
import json
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from ../../server import app

'''
When the delete /reservations endpoint gets called, a user must fill in the license plate (user id is also required, but that can be stored on the backend when a user logs in)
the api will check if the vehicle has a reservation (the reservation wont be cancelled if there is no reservation)
the api will also check if the vehicle and the parking lot the vehicle has a reservation exists
the amount of reservations on a parking lot must also go down by one
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

@dataclass
class Session:
    id: int
    parking_lot_id: int
    payment_id: int
    user_id: int
    vehicle_id: int
    started: date
    stopped: date
    duration_minutes: int
    cost: float

def get_fake_session(id: int) -> Session:
    return [{0, 0, 0, 0, "2020-03-25", "2020-03-25", 30, 1}, {1, 1, 1, 1, "2020-03-25", "2020-03-25", 30, 1}][id]

def get_fake_parking_location(id: int) -> Parking_location:
    return [
        {
            0, 
            "Bedrijventerrein Almere Parkeergarage", 
            "Industrial Zone", 
            "Schanssingel 337, 2421 BS Almere", 
            1, 
            1, 
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
            "test_license_plate",
            "",
            "",
            "",
            2005,
            "2020-03-25"
        }, 
        {
            1,
            0,
            "invalid_parking_lot",
            "",
            "",
            "",
            2005,
            "2020-03-25"
        }
        ][id]
    

reservations: list[Reservation] = []

def fake_delete_reservation(parking_lot_id: int, license_plate: str) -> None:
    for i in range(len(reservations)):
        if reservations[i].parking_lot_id == parking_lot_id:
            if reservations[i].license_plate == license_plate:
                reservations.pop(i)
                break
    

def get_fake_reservations(rid: int)-> Reservation:
    result: Reservation = None
    for res in reservations:
        if res["id"] == rid:
            result = res
    return result

def reset_reservations() -> None:
    reservations.append(Reservation(0, 0, 0, "test_license_plate", ""), Reservation(99999, 0, 0, "invalid_parking_lot", ""))

def create_test_token(username: str) -> str:
    expire: date = datetime.utcnow() + timedelta(minutes=30)
    token: str = jwt.encode({"sub": username, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)
    return token

token: str = create_test_token("test")
valid_header: dict[str, str] = {"Authorization": f"Bearer {token}"}
invalid_header: dict[str, str] = {"Authorization": "Bearer invalid"}

'''
Test succesfully deleting a reservation
'''
@patch("../../controllers/reservation_controller.db_delete_reservation", side_effect=fake_delete_reservation)
@patch("../../controllers/reservation_controller.db_get_parking_locations", side_effect=get_fake_parking_location)
@patch("../../controllers/reservation_controller.db_get_vehicle", side_effect=get_fake_vehicle)
@patch("../../controllers/reservation_controller.db_get_sessions", side_effect=get_fake_session)
def test_delete_reservation() -> None:
    reservation_amount_before = reservations.len()
    response = client.DELETE("/reservations", headers=valid_header, json={"test_license_plate"})
    assert reservations.len() == reservation_amount_before - 1
    assert response.status_code == 200
    reset_reservations()

'''
Test deleting a reservation when not authorized
'''
@patch("../../controllers/reservation_controller.db_delete_reservation", side_effect=fake_delete_reservation)
@patch("../../controllers/reservation_controller.db_get_parking_locations", side_effect=get_fake_parking_location)
@patch("../../controllers/reservation_controller.db_get_vehicle", side_effect=get_fake_vehicle)
@patch("../../controllers/reservation_controller.db_get_sessions", side_effect=get_fake_session)
def test_delete_reservation_when_not_authorized() -> None:
    reservation_amount_before = reservations.len()
    response = client.DELETE("/reservations", headers=invalid_header, json={"test_license_plate"})
    assert reservations.len() == reservation_amount_before
    assert response.status_code == 401
    reset_reservations()

'''
Test deleting a reservation when a vehicle does not exist
'''
@patch("../../controllers/reservation_controller.db_delete_reservation", side_effect=fake_delete_reservation)
@patch("../../controllers/reservation_controller.db_get_parking_locations", side_effect=get_fake_parking_location)
@patch("../../controllers/reservation_controller.db_get_vehicle", side_effect=get_fake_vehicle)
@patch("../../controllers/reservation_controller.db_get_sessions", side_effect=get_fake_session)
def test_delete_reservation_when_vehicle_not_exist() -> None:
    reservation_amount_before = reservations.len()
    response = client.DELETE("/reservations", headers=valid_header, json={"invalid_license_plate"})
    assert reservations.len() == reservation_amount_before
    assert response.status_code == 422
    reset_reservations()

'''
Test deleting a reservation when a vehice has no reservation
'''
@patch("../../controllers/reservation_controller.db_delete_reservation", side_effect=fake_delete_reservation)
@patch("../../controllers/reservation_controller.db_get_parking_locations", side_effect=get_fake_parking_location)
@patch("../../controllers/reservation_controller.db_get_vehicle", side_effect=get_fake_vehicle)
@patch("../../controllers/reservation_controller.db_get_sessions", side_effect=get_fake_session)
def test_delete_reservation() -> None:
    reservation_amount_before = reservations.len()
    response = client.DELETE("/reservations", headers=valid_header, json={"test_license_plate"})
    assert reservations.len() == reservation_amount_before - 1
    assert response.status_code == 200
    response2 = client.DELETE("/reservations", headers=valid_header, json={"test_license_plate"})
    assert reservations.len() == reservation_amount_before - 1
    assert response.status_code == 422
    reset_reservations()

'''
Test deleting a reservation when the parking lot does not exist
'''
@patch("../../controllers/reservation_controller.db_delete_reservation", side_effect=fake_delete_reservation)
@patch("../../controllers/reservation_controller.db_get_parking_locations", side_effect=get_fake_parking_location)
@patch("../../controllers/reservation_controller.db_get_vehicle", side_effect=get_fake_vehicle)
@patch("../../controllers/reservation_controller.db_get_sessions", side_effect=get_fake_session)
def test_delete_reservation() -> None:
    reservation_amount_before = reservations.len()
    response = client.DELETE("/reservations", headers=valid_header, json={"invalid_parking_lot"})
    assert reservations.len() == reservation_amount_before
    assert response.status_code == 422
    reset_reservations()
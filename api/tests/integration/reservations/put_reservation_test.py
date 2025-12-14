from dataclasses import asdict, dataclass
from datetime import date
import json
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from ../../server import app

'''
when the put /reservations endpoint is called, a user must fill in 2 fields: a license plate and the data that must be updated
the api will check if the vehicle has a reservation, and return a 404 if it does not
the api will then check if the data the user has send is valid (whether the park lot exists and if the date is in the future)
lastly, the api will update the reservation
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
            "",
            "",
            "",
            "",
            2005,
            "2020-03-25"
        }
        ][id]
    

reservations: list[Reservation] = []

def fake_put_reservation(reservation: Reservation) -> None:
    for i in range(len(reservations)):
        if reservations[i].parking_lot_id == reservation.parking_lot_id:
            if reservations[i].license_plate == reservation.license_plate:
                reservations.pop(i)
                break
    reservations.append(reservation)

def get_fake_reservations(rid: int)-> Reservation:
    result: Reservation = None
    for res in reservations:
        if res["id"] == rid:
            result = res
    return result

def reset_reservations() -> None:
    reservations.append(Reservation(0, 0, 0, "test_license_plate", ""), Reservation(0, 0, 1, "test_license_plate2", ""))

def create_test_token(username: str) -> str:
    expire: date = datetime.utcnow() + timedelta(minutes=30)
    token: str = jwt.encode({"sub": username, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)
    return token

token: str = create_test_token("test")
valid_header: dict[str, str] = {"Authorization": f"Bearer {token}"}
invalid_header: dict[str, str] = {"Authorization": "Bearer invalid"}

'''
Test successfully updating a reservation
'''
@patch("../../controllers/reservation_controller.db_post_reservation", side_effect=fake_put_reservation)
@patch("../../controllers/reservation_controller.db_get_parking_locations", side_effect=get_fake_parking_location)
@patch("../../controllers/reservation_controller.db_get_vehicle", side_effect=get_fake_vehicle)
@patch("../../controllers/reservation_controller.db_get_sessions", side_effect=get_fake_session)
def test_successfully_update_reservation() -> None:
    reservation_amount_before = reservations.len()
    assert reservations[0].parking_lot_id == 0

    data: Reservation = Reservation(1, 1, 1, "test_license_plate", str(date.today()))
    response = client.put("/reservations", headers=valid_header, json={"test_license_plate", asdict(data)})

    assert response.status_code == 200
    assert len(reservations) == reservation_amount_before
    assert reservations[0].parking_lot_id == 1
    reset_reservations()

'''
Test updating a reservation when not authorized
'''
@patch("../../controllers/reservation_controller.db_post_reservation", side_effect=fake_put_reservation)
@patch("../../controllers/reservation_controller.db_get_parking_locations", side_effect=get_fake_parking_location)
@patch("../../controllers/reservation_controller.db_get_vehicle", side_effect=get_fake_vehicle)
@patch("../../controllers/reservation_controller.db_get_sessions", side_effect=get_fake_session)
def test_update_reservation_not_authorized() -> None:
    reservation_amount_before = reservations.len()
    assert reservations[0].parking_lot_id == 0

    data: Reservation = Reservation(1, 1, 1, "test_license_plate", str(date.today()))
    response = client.put("/reservations", headers=invalid_header, json={"test_license_plate", asdict(data)})

    assert response.status_code == 200
    assert len(reservations) == reservation_amount_before
    assert reservations[0].parking_lot_id == 0
    reset_reservations()

'''
Test updating a reservation when not all data is filled in
'''

@patch("../../controllers/reservation_controller.db_post_reservation", side_effect=fake_put_reservation)
@patch("../../controllers/reservation_controller.db_get_parking_locations", side_effect=get_fake_parking_location)
@patch("../../controllers/reservation_controller.db_get_vehicle", side_effect=get_fake_vehicle)
@patch("../../controllers/reservation_controller.db_get_sessions", side_effect=get_fake_session)
def test_update_reservation_incomplete_data() -> None:
    reservation_amount_before = reservations.len()
    assert reservations[0].parking_lot_id == 0
    response = client.put("/reservations", headers=valid_header, json={"test_license_plate", {"parking_lot_id": 1}})

    assert response.status_code == 200
    assert len(reservations) == reservation_amount_before
    assert reservations[0].parking_lot_id == 1
    reset_reservations()

'''
Test updating a reservation with an invalid license plate
'''
@patch("../../controllers/reservation_controller.db_post_reservation", side_effect=fake_put_reservation)
@patch("../../controllers/reservation_controller.db_get_parking_locations", side_effect=get_fake_parking_location)
@patch("../../controllers/reservation_controller.db_get_vehicle", side_effect=get_fake_vehicle)
@patch("../../controllers/reservation_controller.db_get_sessions", side_effect=get_fake_session)
def test_update_reservation_invalid_license_plate() -> None:
    reservation_amount_before = reservations.len()
    assert reservations[0].parking_lot_id == 0

    data: Reservation = Reservation(1, 1, 1, "aaaaa", str(date.today()))
    response = client.put("/reservations", headers=valid_header, json={"invalid_license_plate", asdict(data)})

    assert response.status_code == 404
    assert len(reservations) == reservation_amount_before
    assert reservations[0].parking_lot_id == 0
    reset_reservations()

'''
Test updating a reservation with an invalid parking lot
'''
@patch("../../controllers/reservation_controller.db_post_reservation", side_effect=fake_put_reservation)
@patch("../../controllers/reservation_controller.db_get_parking_locations", side_effect=get_fake_parking_location)
@patch("../../controllers/reservation_controller.db_get_vehicle", side_effect=get_fake_vehicle)
@patch("../../controllers/reservation_controller.db_get_sessions", side_effect=get_fake_session)
def test_update_reservation_invalid_license_plate() -> None:
    reservation_amount_before = reservations.len()
    assert reservations[0].parking_lot_id == 0

    data: Reservation = Reservation(99999, 1, 1, "test_license_plate", str(date.today()))
    response = client.put("/reservations", headers=valid_header, json={"test_license_plate", asdict(data)})

    assert response.status_code == 404
    assert len(reservations) == reservation_amount_before
    assert reservations[0].parking_lot_id == 0
    reset_reservations()

'''
Test updating a reservation when the date is set to the past
'''
@patch("../../controllers/reservation_controller.db_post_reservation", side_effect=fake_put_reservation)
@patch("../../controllers/reservation_controller.db_get_parking_locations", side_effect=get_fake_parking_location)
@patch("../../controllers/reservation_controller.db_get_vehicle", side_effect=get_fake_vehicle)
@patch("../../controllers/reservation_controller.db_get_sessions", side_effect=get_fake_session)
def test_update_reservation_invalid_license_plate() -> None:
    reservation_amount_before = reservations.len()
    assert reservations[0].started == date.today()

    data: Reservation = Reservation(99999, 1, 1, "test_license_plate", str(date.today() - 1))
    response = client.put("/reservations", headers=valid_header, json={"test_license_plate", asdict(data)})

    assert response.status_code == 404
    assert len(reservations) == reservation_amount_before
    assert reservations[0].started == date.today()
    reset_reservations()
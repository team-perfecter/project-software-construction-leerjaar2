from dataclasses import dataclass
from datetime import date


@dataclass
class Parking_lot:
    id: int
    name: str
    location: str
    address: str
    capacity: int
    reserved: int
    tariff: float
    daytariff: float
    created_at: date
    lat: float
    lng: float


""" data
json
"1": {
        "id": "1",
        "name": "Bedrijventerrein Almere Parkeergarage",
        "location": "Industrial Zone",
        "address": "Schanssingel 337, 2421 BS Almere",
        "capacity": 335,
        "reserved": 77,
        "tariff": 1.9,
        "daytariff": 11,
        "created_at": "2020-03-25",
        "coordinates": {
            "lat": 52.3133,
            "lng": 5.2234
        }
    }
db
"id": "1",
"name": "Bedrijventerrein Almere Parkeergarage",
"location": "Industrial Zone",
"address": "Schanssingel 337, 2421 BS Almere",
"capacity": 335,
"reserved": 77,
"tariff": 1.9,
"daytariff": 11,
"created_at": "2020-03-25",
"lat": 52.3133,
"lng": 5.2234
"""

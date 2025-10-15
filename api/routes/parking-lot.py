from dataclasses import dataclass
from datetime import date

from fastapi import FastAPI

#TODO? moet door Stelain een ok krijgen nadat server.py gerefactored is (versie 1.0 klaar is)

app = FastAPI()

@dataclass
class Parkinglot:
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

# POST
# TODO: create parking lot (admin only)             /parking-lots
# TODO: start parking session by lid                /parking-lots/{lid}/sessions/start
# TODO: end parking session by lid                  /parking-lots/{lid}/sessions/stop

# GET
# TODO: get all parking lots                        /parking-lots/
# TODO: get parking lot by lid                      /parking-lots/{lid}
# TODO: get all sessions lot by lid (admin only)    /parking-lots/{lid}/sessions
# TODO: get session by session sid (admin only)     /parking-lots/{lid}/sessions/{sid}
# region extra
# TODO?: get parking lots availability               /parking-lots/availability
# TODO?: get parking lot availability by id          /parking-lots/{id}/availability
# TODO?: search parking lots                         /parking-lots/search
# TODO?: get parking lots by city                    /parking-lots/city/{city}
# TODO?: get parking lots by location                /parking-lots/location/{location}
# TODO?: get parking lot reservations                /parking-lots/{id}/reservations
# TODO?: get parking lot stats (admin only)          /parking-lots/{id}/stats
# endregion

# PUT
# TODO: update parking lot by lid (admin only)      /parking-lots/{lid}

# DELETE
# TODO: delete parking lot by lid (admin only)      /parking-lots/{lid}
# TODO: delete session by session lid (admin only)  /parking-lots/{lid}/sessions/{sid}
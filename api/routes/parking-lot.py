from dataclasses import dataclass
from datetime import date

from fastapi import FastAPI, HTTPException

# TODO? moet door Stelain een ok krijgen nadat server.py gerefactored is (versie 1.0 klaar is)

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


parking_lot_list: list[Parkinglot] = [
    Parkinglot(
        id=1,
        name="Bedrijventerrein Almere Parkeergarage",
        location="Industrial Zone",
        address="Schanssingel 337, 2421 BS Almere",
        capacity=335,
        reserved=77,
        tariff=1.9,
        daytariff=11.0,
        created_at=date(2020, 3, 25),
        lat=52.3133,
        lng=5.2234,
    ),
    Parkinglot(
        id=2,
        name="Centrum Parkeergarage",
        location="City Center",
        address="Hoofdstraat 123, 1234 AB Amsterdam",
        capacity=200,
        reserved=45,
        tariff=2.5,
        daytariff=15.0,
        created_at=date(2021, 5, 10),
        lat=52.3676,
        lng=4.9041,
    ),
]

# POST
# TODO: create parking lot (admin only)             /parking-lots
# TODO: start parking session by lid                /parking-lots/{lid}/sessions/start
# Authenticatie: Vereist
# Body: {"licenseplate": "XX-XX-XX"}
# Validatie: check of er al een actieve session is voor dat kenteken

# TODO: end parking session by lid                  /parking-lots/{lid}/sessions/stop


# GET
# TODO: get all parking lots                        /parking-lots/
@app.get("/parking-lots/")
async def get_all_parking_lots():
    return parking_lot_list

# TODO: get parking lot by lid                      /parking-lots/{lid}
@app.get("/parking-lots/{lid}")
async def get_parking_lot_by_lid(lid: int):
    for lot in parking_lot_list:
        if lot.id == lid:
            return lot
    raise HTTPException(
        status_code=404,
        detail={
            "error": "Not Found",
            "message": f"Parking lot with ID {lid} does not exist",
            "code": "PARKING_LOT_NOT_FOUND",
        },
    )



# TODO: get all sessions lot by lid (admin only)    /parking-lots/{lid}/sessions
# TODO: get session by session sid (admin only)     /parking-lots/{lid}/sessions/{sid}
# region extra
# TODO? PO ok maar eerst de rest: get parking lots availability               /parking-lots/availability
# TODO? PO ok maar eerst de rest: get parking lot availability by id          /parking-lots/{id}/availability
# TODO? PO ok maar eerst de rest: search parking lots                         /parking-lots/search
# TODO? PO ok maar eerst de rest: get parking lots by city                    /parking-lots/city/{city}
# TODO? PO ok maar eerst de rest: get parking lots by location                /parking-lots/location/{location}
# TODO? PO ok maar eerst de rest: get parking lot reservations                /parking-lots/{id}/reservations
# TODO? PO ok maar eerst de rest: get parking lot stats (admin only)          /parking-lots/{id}/stats
# endregion

# PUT
# TODO: update parking lot by lid (admin only)      /parking-lots/{lid}

# DELETE
# TODO: delete parking lot by lid (admin only)      /parking-lots/{lid}
# TODO: delete session by session lid (admin only)  /parking-lots/{lid}/sessions/{sid}

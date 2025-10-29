from dataclasses import dataclass
from datetime import date
from datatypes.parkinglot import Parkinglot

from fastapi import FastAPI, HTTPException, status

# TODO? moet door Stelain een ok krijgen nadat server.py gerefactored is (versie 1.0 klaar is)

app = FastAPI()


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
@app.post("/parking-lots")
async def create_parking_lot(parking_lot: Parkinglot):
    parking_lot_list.append(parking_lot)
    return parking_lot

@app.post("/parking-lots", status_code=status.HTTP_201_CREATED)
async def create_parking_lot(parking_lot: Parkinglot):
    # Validate that name is not empty
    if not parking_lot.name.strip():
        raise HTTPException(
            status_code=400,
            detail="Parking lot name cannot be empty"
        )
    
    # Generate a new ID
    new_id = max([lot.id for lot in parking_lot_list], default=0) + 1
    parking_lot.id = new_id
    
    parking_lot_list.append(parking_lot)
    return parking_lot

# TODO: start parking session by lid                /parking-lots/{lid}/sessions/start
# Authenticatie: Vereist
# Body: {"licenseplate": "XX-XX-XX"}
# Validatie: check of er al een actieve session is voor dat kenteken

# TODO: end parking session by lid                  /parking-lots/{lid}/sessions/stop


# GET
# TODO: get all parking lots                        /parking-lots/
@app.get("/parking-lots/")
async def get_all_parking_lots():
    if len(parking_lot_list) == 0:
        raise HTTPException(
            status_code=204,
            detail={
                "error": "No Content",
                "message": f"There are no parking lots",
                "code": "PARKING_LOT_NOT_FOUND",
            },
        )
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

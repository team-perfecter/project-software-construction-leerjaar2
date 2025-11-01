import os
from dataclasses import dataclass
from datetime import date, datetime
from profile import get_current_user, require_admin

from api.storage.profile_storage import Profile_storage
from api.storage_utils import *
from api.datatypes.parking_lot import Parkinglot
from datatypes.session_requests import SessionStartRequest, SessionStopRequest
from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel


users_modal: Profile_storage = Profile_storage()
    
# TODO? moet door Stelain een ok krijgen nadat server.py gerefactored is (versie 1.0 klaar is) hij zei oke

app = FastAPI()

temp_login_id = 2
auth = list(filter(lambda user: user["id"] == temp_login_id, users_modal.get_all_users()))[0]


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


# region POST
# TODO: create parking lot (admin only)             /parking-lots
@app.post("/parking-lots", status_code=status.HTTP_201_CREATED)
async def create_parking_lot(parking_lot: Parkinglot):
    # Check if admin
    if auth["role"] == "ADMIN":
        if not parking_lot.name.strip():
            raise HTTPException(status_code=400, detail="Parking lot name cannot be empty")

        new_id = max([lot.id for lot in parking_lot_list], default=0) + 1
        parking_lot.id = new_id

        parking_lot_list.append(parking_lot)
        return parking_lot
    else:
        return "Something went wrong."




# TODO: start parking session by lid                /parking-lots/{lid}/sessions/start
# Authenticatie: Vereist
# Body: {"licenseplate": "XX-XX-XX"}
# Validatie: check of er al een actieve session is voor dat kenteken
@app.post("/parking-lots/{lid}/sessions/start")
async def start_parking_session(lid: int, request: SessionStartRequest):
    # Check if admin
    # Check if parking lot exists
    parking_lot = None
    for lot in parking_lot_list:
        if lot.id == lid:
            parking_lot = lot
            break
    if not parking_lot:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Parking lot not found",
                "message": f"Parking lot with ID {lid} does not exist",
            },
        )

    # Load existing sessions for this parking lot
    # Check if there's already an active session for this license plate
    # Create new session
    # Save sessions back to file


# TODO: end parking session by lid                  /parking-lots/{lid}/sessions/stop
def stop_parking_session(lid: int, request: SessionStopRequest):
    # Check if admin

    # Check if parking lot exists
    parking_lot = None
    for lot in parking_lot_list:
        if lot.id == lid:
            parking_lot = lot
            break
    if not parking_lot:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Parking lot not found",
                "message": f"Parking lot with ID {lid} does not exist",
            },
        )

    # Load existing sessions for this parking lot
    # Find active session for this license plate
    # Calculate total fee based on duration and tariff
    # Mark session as ended
    # Save sessions back to file


# endregion


# region GET
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
# endregion
# region PUT
# TODO: update parking lot by lid (admin only)      /parking-lots/{lid}
def update_parking_lot(lid: int, updated_lot: Parkinglot):
    pass


# endregion


# region DELETE
# TODO: delete parking lot by lid (admin only)      /parking-lots/{lid}
@app.delete("/parking-lots/{lid}")
async def delete_parking_lot(
    lid: int,
    current_user: str = Depends(get_current_user),
    admin_user: str = Depends(require_admin),
):
    # Find parking lot in the list later db
    parking_lot = None
    parking_lot_index = None

    for index, lot in enumerate(parking_lot_list):
        if lot.id == lid:
            parking_lot = lot
            parking_lot_index = index
            break

    if not parking_lot:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Parking lot not found",
                "message": f"Parking lot with ID {lid} does not exist",
                "code": "PARKING_LOT_NOT_FOUND",
            },
        )

    # Check if there are active sessions for this parking lot
    # If sessions file doesn't exist or can't be read, continue with deletion

    # Remove parking lot from the list
    parking_lot_list.pop(parking_lot_index)

    return {
        "message": f"Parking lot '{parking_lot.name}' with ID {lid} has been successfully deleted",
        "deleted_parking_lot": {
            "id": parking_lot.id,
            "name": parking_lot.name,
            "location": parking_lot.location,
        },
    }


# TODO: delete session by session lid (admin only)  /parking-lots/{lid}/sessions/{sid}
@app.delete("/parking-lots/{lid}/sessions/{sid}")
async def delete_parking_session(
    lid: int,
    sid: int,
    current_user: str = Depends(get_current_user),
    admin_user: str = Depends(require_admin),
):
    # Check if parking lot exists
    parking_lot = None
    for lot in parking_lot_list:
        if lot.id == lid:
            parking_lot = lot
            break

    if not parking_lot:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Parking lot not found",
                "message": f"Parking lot with ID {lid} does not exist",
                "code": "PARKING_LOT_NOT_FOUND",
            },
        )

    # Load sessions for this parking lot

    # Check if session exists

    # Get session details before deletion

    # Remove session

    # Save updated sessions back to file

    # return {
    #     "message": f"Session {sid} has been successfully deleted from parking lot {lid}",
    #     "deleted_session": deleted_session,
    # }


# endregion

import os
import logging
from datetime import date, datetime
from api.models.parking_lot_model import ParkingLotModel
from api.storage_utils import *
from api.datatypes.parking_lot import Parking_lot, Parking_lot_create
from api.datatypes.user import User
from api.auth_utils import get_current_user
from fastapi import APIRouter, HTTPException, status, Depends

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

router = APIRouter(tags=["parking lot"])

parking_lot_model: ParkingLotModel = ParkingLotModel()


# region POST
# TODO: create parking lot (admin only)             /parking-lots
@router.post("/parking-lots", status_code=status.HTTP_201_CREATED)
async def create_parking_lot(
    parking_lot_data: Parking_lot_create,
    current_user: User = Depends(get_current_user),
):
    logging.info(
        "User with id %i attempting to create a new parking lot", current_user.id
    )

    # # Check if user is admin
    # if current_user.role != "ADMIN":
    #     logging.warning(
    #         "Access denied for user with id %i - not an admin", current_user.id
    #     )
    #     raise HTTPException(
    #         status_code=403, detail="Access denied. Admin privileges required."
    #     )

    # later validatie toevoegen?
    parking_lots = parking_lot_model.get_all_parking_lots()
    new_id = max([lot.id for lot in parking_lots], default=0) + 1

    # Maak een volledig Parking_lot object met gegenereerde velden
    parking_lot = Parking_lot(
        id=new_id,
        name=parking_lot_data.name,
        location=parking_lot_data.location,
        address=parking_lot_data.address,
        capacity=parking_lot_data.capacity,
        reserved=0,  # Nieuwe parking lot start met 0 reserveringen
        tariff=parking_lot_data.tariff,
        daytariff=parking_lot_data.daytariff,
        created_at=date.today(),
        lat=parking_lot_data.lat,
        lng=parking_lot_data.lng,
    )

    logging.info(
        "Creating parking lot with id %i and name '%s'", new_id, parking_lot.name
    )
    parking_lot_model.create_parking_lot(parking_lot)
    logging.info("Successfully created parking lot with id %i", new_id)
    return parking_lot


# endregion


# region GET
# TODO: get all parking lots                        /parking-lots/
@router.get("/parking-lots/")
async def get_all_parking_lots():
    logging.info("Retrieving all parking lots")
    parking_lots = parking_lot_model.get_all_parking_lots()
    if len(parking_lots) == 0:
        logging.warning("No parking lots found in the system")
        raise HTTPException(
            status_code=204,
            detail={
                "error": "No Content",
                "message": f"There are no parking lots",
                "code": "PARKING_LOT_NOT_FOUND",
            },
        )
    logging.info("Successfully retrieved %i parking lots", len(parking_lots))
    return parking_lots


# TODO: get parking lot by lid                      /parking-lots/{lid}
@router.get("/parking-lots/{lid}")
async def get_parking_lot_by_lid(
    lid: int, current_user: User = Depends(get_current_user)
):
    logging.info(
        "User with id %i retrieving parking lot with id %i", current_user.id, lid
    )
    parking_lot = parking_lot_model.get_parking_lot_by_lid(lid)
    if parking_lot:
        logging.info("Successfully retrieved parking lot with id %i", lid)
        return parking_lot

    logging.warning("Parking lot with id %i does not exist", lid)
    raise HTTPException(
        status_code=404,
        detail={
            "error": "Not Found",
            "message": f"Parking lot with ID {lid} does not exist",
            "code": "PARKING_LOT_NOT_FOUND",
        },
    )


# TODO: get all sessions lot by lid (admin only)    /parking-lots/{lid}/sessions
@router.get("/parking-lots/{lid}/sessions")
async def get_all_sessions_by_lid(
    lid: int, current_user: User = Depends(get_current_user)
):
    logging.info(
        "User with id %i retrieving all sessions from parking lot with id %i",
        current_user.id,
        lid,
    )

    # Check if user is admin
    # if current_user.role != "ADMIN":
    #     logging.warning(
    #         "Access denied for user with id %i - not an admin", current_user.id
    #     )
    #     raise HTTPException(
    #         status_code=403, detail="Access denied. Admin privileges required."
    #     )

    parking_lot = parking_lot_model.get_parking_lot_by_lid(lid)
    if not parking_lot:
        logging.warning("Parking lot with id %i does not exist", lid)
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Parking lot not found",
                "message": f"Parking lot with ID {lid} does not exist",
                "code": "PARKING_LOT_NOT_FOUND",
            },
        )

    logging.info("Retrieving all sessions for parking lot with id %i", lid)
    sessions = parking_lot_model.get_all_sessions_by_lid(lid)
    logging.info(
        "Successfully retrieved %i sessions for parking lot with id %i",
        len(sessions),
        lid,
    )
    return sessions


# TODO: get session by session sid (admin only)     /parking-lots/{lid}/sessions/{sid}
@router.get("/parking-lots/{lid}/sessions/{sid}")
async def get_session_by_lid_and_sid(
    lid: int,
    sid: int,
    current_user: User = Depends(get_current_user),
):
    logging.info(
        "User with id %i retrieving session %i from parking lot %i",
        current_user.id,
        sid,
        lid,
    )

    # Check if user is admin
    # if current_user.role != "ADMIN":
    #     logging.warning(
    #         "Access denied for user with id %i - not an admin", current_user.id
    #     )
    #     raise HTTPException(
    #         status_code=403, detail="Access denied. Admin privileges required."
    #     )

    parking_lot = parking_lot_model.get_parking_lot_by_lid(lid)
    if not parking_lot:
        logging.warning("Parking lot with id %i does not exist", lid)
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Parking lot not found",
                "message": f"Parking lot with ID {lid} does not exist",
                "code": "PARKING_LOT_NOT_FOUND",
            },
        )

    logging.info("Retrieving session %i for parking lot with id %i", sid, lid)
    session = parking_lot_model.get_session_by_lid_and_sid(lid, sid)
    if session:
        logging.info(
            "Successfully retrieved session %i for parking lot with id %i", sid, lid
        )
        return session

    logging.warning(
        "Session %i does not exist for parking lot with id %i", sid, lid
    )
    raise HTTPException(
        status_code=404,
        detail={
            "error": "Session not found",
            "message": f"Session with ID {sid} does not exist for parking lot {lid}",
            "code": "SESSION_NOT_FOUND",
        },
    )

# region extra
# TODO? moet door Stelain een ok krijgen nadat server.py gerefactored is (versie 1.0 klaar is) hij zei oke
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
@router.put("/parking-lots/{lid}")
async def update_parking_lot(
    lid: int, updated_lot: Parking_lot, current_user: User = Depends(get_current_user)
):
    logging.info(
        "User with id %i attempting to update parking lot with id %i",
        current_user.id,
        lid,
    )

    # Check if user is admin
    if current_user.role != "ADMIN":
        logging.warning(
            "Access denied for user with id %i - not an admin", current_user.id
        )
        raise HTTPException(
            status_code=403, detail="Access denied. Admin privileges required."
        )

    # TODO: Implement update logic
    pass


# endregion


# region DELETE
# TODO: delete parking lot by lid (admin only)      /parking-lots/{lid}
@router.delete("/parking-lots/{lid}")
async def delete_parking_lot(
    lid: int,
    current_user: User = Depends(get_current_user),
):
    logging.info(
        "User with id %i attempting to delete parking lot with id %i",
        current_user.id,
        lid,
    )

    if current_user.role != "ADMIN":
        logging.warning(
            "Access denied for user with id %i - not an admin", current_user.id
        )
        raise HTTPException(
            status_code=403, detail="Access denied. Admin privileges required."
        )

    # Find parking lot
    parking_lot = parking_lot_model.get_parking_lot_by_lid(lid)

    if not parking_lot:
        logging.warning("Parking lot with id %i does not exist", lid)
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
    # Delete parking lot
    logging.info("Deleting parking lot '%s' with id %i", parking_lot.name, lid)
    success = parking_lot_model.delete_parking_lot(lid)
    if not success:
        logging.error("Failed to delete parking lot with id %i", lid)
        raise HTTPException(status_code=500, detail="Failed to delete parking lot")

    logging.info(
        "Successfully deleted parking lot '%s' with id %i", parking_lot.name, lid
    )
    return {
        "message": f"Parking lot '{parking_lot.name}' with ID {lid} has been successfully deleted",
        "deleted_parking_lot": {
            "id": parking_lot.id,
            "name": parking_lot.name,
            "location": parking_lot.location,
        },
    }


# TODO: delete session by session lid (admin only)  /parking-lots/{lid}/sessions/{sid}
@router.delete("/parking-lots/{lid}/sessions/{sid}")
async def delete_parking_session(
    lid: int,
    sid: int,
    current_user: User = Depends(get_current_user),
):
    logging.info(
        "User with id %i attempting to delete session %i from parking lot %i",
        current_user.id,
        sid,
        lid,
    )

    # Check if user is admin
    if current_user.role != "ADMIN":
        logging.warning(
            "Access denied for user with id %i - not an admin", current_user.id
        )
        raise HTTPException(
            status_code=403, detail="Access denied. Admin privileges required."
        )

    # Check if parking lot exists
    parking_lot = parking_lot_model.get_parking_lot_by_lid(lid)

    if not parking_lot:
        logging.warning("Parking lot with id %i does not exist", lid)
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Parking lot not found",
                "message": f"Parking lot with ID {lid} does not exist",
                "code": "PARKING_LOT_NOT_FOUND",
            },
        )

    logging.info("Deleting session %i from parking lot %i", sid, lid)
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

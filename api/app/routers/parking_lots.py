"""
This file contains all endpoints related to parking lots.
"""

import logging
from datetime import date
from fastapi import APIRouter, HTTPException, status, Depends
from api.models.parking_lot_model import ParkingLotModel
from api.datatypes.parking_lot import ParkingLot, ParkingLotCreate, ParkingLotFilter
from api.datatypes.user import User, UserRole
from api.auth_utils import get_current_user, require_role


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

router = APIRouter(tags=["parking lot"])

parking_lot_model: ParkingLotModel = ParkingLotModel()

def get_lot_if_exists(lid: int):
    """Gets a parking lot based on a specific lot id. 

    Args:
        lid (int): The id of the parking lot.

    Returns:
        ParkingLot: Information about the requested parking lot.

    Raises:
        HTTPException: Raises 404 if there are no parking lots with the specified id.
    """
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
        }
    )

# region POST
@router.post("/parking-lots", status_code=status.HTTP_201_CREATED)
async def create_parking_lot(
    parking_lot_data: ParkingLotCreate,
    _: User = Depends(require_role(UserRole.SUPERADMIN)),
):
    """Creates a new parking lot based on provided data. 

    Args:
        parking_lot_data (ParkingLotCreate): The information about the parking lot.
        _ (User): Checks if the logged in user is a super admin.

    Returns:
        ParkingLot: The information about the newly created parking lot.

    Raises:
        HTTPException: Raises 500 if there is an error in creating a new parking lot.
        HTTPException: Raises 403 if the logged in user is not a super admin.
        HTTPException: Raises 401 if there is no user logged in.
    """
    # logging.info(
    #     "User with id %i attempting to create a new parking lot", current_user.id
    # )

    logging.debug("Generating new ID for parking lot")
    parking_lots = parking_lot_model.get_all_parking_lots()
    new_id = max([lot.id for lot in parking_lots], default=0) + 1
    logging.debug("Generated new parking lot ID: %i", new_id)

    logging.debug(
        "Creating parking lot object with data: name='%s', location='%s', capacity=%i",
        parking_lot_data.name,
        parking_lot_data.location,
        parking_lot_data.capacity,
    )

    parking_lot = ParkingLot(
        id=new_id,
        name=parking_lot_data.name,
        location=parking_lot_data.location,
        address=parking_lot_data.address,
        capacity=parking_lot_data.capacity,
        reserved=0,
        tariff=parking_lot_data.tariff,
        daytariff=parking_lot_data.daytariff,
        created_at=date.today(),
        lat=parking_lot_data.lat,
        lng=parking_lot_data.lng,
        status=parking_lot_data.status or "open",
        closed_reason=parking_lot_data.closed_reason,
        closed_date=parking_lot_data.closed_date,
    )

    logging.info(
        "Creating parking lot with id %i and name '%s' at location '%s'",
        new_id,
        parking_lot.name,
        parking_lot.location,
    )

    try:
        parking_lot_model.create_parking_lot(parking_lot)
        logging.info("Successfully created parking lot with id %i in database", new_id)

    except Exception as e:
        logging.error("Failed to create parking lot in database: %s", str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal Server Error",
                "message": "Failed to create parking lot",
                "code": "CREATE_FAILED",
            },
        )

    # logging.info("Parking lot creation completed successfully for user %i", current_user.id)
    return parking_lot


# endregion


# region GET
@router.get("/parking-lots/")
async def get_all_parking_lots():
    """Returns a list of all parking lots. 

    Returns:
        [ParkingLot]: Information about all the parking lots.

    Raises:
        HTTPException: Raises 204 if there are no parking lots in the system.
    """
    logging.info("Retrieving all parking lots")
    parking_lots = parking_lot_model.get_all_parking_lots()
    if len(parking_lots) == 0:
        logging.warning("No parking lots found in the system")
        raise HTTPException(
            status_code=204,
            detail={
                "error": "No Content",
                "message": "There are no parking lots",
                "code": "PARKING_LOT_NOT_FOUND",
            },
        )
    logging.info("Successfully retrieved %i parking lots", len(parking_lots))
    return parking_lots


@router.get("/parking-lots/{lid}")
async def get_parking_lot_by_lid(lid: int):
    """Gets a parking lot based on a specific lot id. 

    Args:
        lid (int): The id of the parking lot.

    Returns:
        ParkingLot: Information about the requested parking lot.
    """
    # logging.info(
    #     "User with id %i retrieving parking lot with id %i", current_user.id, lid
    # )
    return get_lot_if_exists(lid)




@router.get("/parking-lots/{lid}/sessions")
async def get_all_sessions_by_lid(
    lid: int,
    _: User = Depends(require_role(UserRole.SUPERADMIN)),
):
    """Gets all sessions of a specified parking lot. 

    Args:
        lid (int): The id of the parking lot.
        _ (User): Checks if the logged in user is a super admin

    Returns:
        [Session]: Information about all the sessions of a specified parking lot.

    Raises:
        HTTPException: Raises 404 if there are no parking lots with the specified id.
        HTTPException: Raises 403 if the logged in user is not a super admin.
        HTTPException: Raises 401 if there is no user logged in.
    """
    # logging.info(
    #     "User with id %i retrieving all sessions from parking lot with id %i",
    #     current_user.id,
    #     lid,
    # )

    _ = get_lot_if_exists(lid)

    logging.info("Retrieving all sessions for parking lot with id %i", lid)
    sessions = parking_lot_model.get_all_sessions_by_lid(lid)
    logging.info(
        "Successfully retrieved %i sessions for parking lot with id %i",
        len(sessions),
        lid,
    )
    return sessions


@router.get("/parking-lots/{lid}/sessions/{sid}")
async def get_session_by_lid_and_sid(
    lid: int,
    sid: int,
    _: User = Depends(require_role(UserRole.SUPERADMIN)),
):
    """Retrieves a specific session from a specific parking lot. 

    Args:
        lid (int): The id of the parking lot.
        sid (int): The id of the session.
        _ (User): Checks if the logged in user is a super admin.

    Returns:
        Session: Information about the specified session.

    Raises:
        HTTPException: Raises 404 if the specified session does not exist.
        HTTPException: Raises 403 if the logged in user is not a super admin.
        HTTPException: Raises 401 if there is no user logged in.
    """
    # logging.info(
    #     "User with id %i retrieving session %i from parking lot %i",
    #     current_user.id,
    #     sid,
    #     lid,
    # )

    _ = get_lot_if_exists(lid)

    logging.info("Retrieving session %i for parking lot with id %i", sid, lid)
    session = parking_lot_model.get_session_by_lid_and_sid(lid, sid)
    if session:
        logging.info(
            "Successfully retrieved session %i for parking lot with id %i", sid, lid
        )
        return session

    logging.warning("Session %i does not exist for parking lot with id %i", sid, lid)
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


@router.get("/parking-lots/location/{location}")
async def get_parking_lots_by_location(
    location: str
):
    """Retrieves all parking lots of a specified location. 

    Args:
        location (str): The location of the parking lots.

    Returns:
        [ParkingLot]: Information about all the parking lots in the specified location.

    Raises:
        HTTPException: Raises 404 if there are no parking lots at the specified location.
    """
    # logging.info(
    #     "User with id %i retrieving parking lots in location: %s",
    #     current_user.id,
    #     location,
    # )
    filters: ParkingLotFilter = ParkingLotFilter(location=location)
    parking_lots = parking_lot_model.find_parking_lots(filters=filters)

    if len(parking_lots) == 0:
        logging.warning("No parking lots found in location: %s", location)
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Not Found",
                "message": f"No parking lots found in location: {location}",
                "code": "PARKING_LOT_NOT_FOUND",
            },
        )

    logging.info(
        "Successfully retrieved %i parking lots in location: %s",
        len(parking_lots),
        location,
    )
    return parking_lots


# TODO? PO ok maar eerst de rest: get parking lot reservations       /parking-lots/{id}/reservations
# TODO? PO ok maar eerst de rest: get parking lot stats (admin only) /parking-lots/{id}/stats
# endregion
# endregion


# region PUT
@router.put("/parking-lots/{lid}")
async def update_parking_lot(
    lid: int,
    updated_lot: ParkingLotCreate,
    _: User = Depends(require_role(UserRole.SUPERADMIN)),
):
    """Updates the information about the specified parking lot. 

    Args:
        lid (int): The id of the parking lot to be updated.
        updated_lot (ParkingLotCreate): The new information of the parking lot.
        _ (User): Checks if the logged in user is a super admin.

    Returns:
        ParkingLotCreate: Information of the updated parking lot.

    Raises:
        HTTPException: Raises 500 if there is an error when updateng the parking lot.
        HTTPException: Raises 403 if the logged in user is not a super admin.
        HTTPException: Raises 401 if there is no user logged in.
    """
    # logging.info(
    #     "User with id %i attempting to update parking lot with id %i",
    #     current_user.id,
    #     lid,
    # )

    logging.debug("Checking if parking lot %i exists", lid)
    parking_lot = get_lot_if_exists(lid)

    if parking_lot.capacity != updated_lot.capacity:
        logging.info(
            "Updating parking lot '%s' (capacity: %i -> %i)",
            parking_lot.name,
            parking_lot.capacity,
            updated_lot.capacity,
        )
    logging.debug("Attempting database update for parking lot %i", lid)

    try:
        success = parking_lot_model.update_parking_lot(lid, updated_lot)
        if not success:
            logging.error(
                "Database update failed for parking lot %i - no rows affected", lid
            )
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Internal Server Error",
                    "message": "Failed to update parking lot",
                    "code": "UPDATE_FAILED",
                },
            )

        logging.info("Successfully updated parking lot with id %i", lid)
        return {
            "message": "Parking lot updated successfully",
            "parking_lot_id": lid,
            "updated_lot": updated_lot,
        }

    except Exception as e:
        logging.error("Exception during parking lot %i update: %s", lid, str(e))
        raise HTTPException(status_code=500, detail="Database error occurred")


@router.put("/parking-lots/{lid}/status")
async def update_parking_lot_status(
    lid: int,
    lot_status: str,
    closed_reason: str = None,
    closed_date: date = None,
    _: User = Depends(get_current_user),
    __: None = Depends(require_role(UserRole.SUPERADMIN)),  # Access check only
):
    """Updates the status of the specified parking lot. 

    Args:
        lid (int): The id of the parking lot.
        lot_status (str): The new status of the parking lot.
        closed_reason (str): The reason why a parking lot is set to closed.
        closed_date (date): The date of when the parking lot was closed.
        _ (User): Checks if there is a user logged in.
        __ (None): Checks if the logged in user is a super admin.

    Returns:
        dict[str, str]: The new status of the parking lot.

    Raises:
        HTTPException: Raises 500 if there is an error when updateng the parking lot.
        HTTPException: Raises 400 if the provided data is invalid.
        HTTPException: Raises 403 if the logged in user is not a super admin.
        HTTPException: Raises 401 if there is no user logged in.
    """
    # logging.info(
    #     "User with id %i attempting to update status of parking lot %i to '%s'",
    #     current_user.id,
    #     lid,
    #     status,
    # )

    parking_lot = get_lot_if_exists(lid)

    valid_statuses = ["open", "closed", "deleted", "maintenance", "full"]
    if lot_status not in valid_statuses:
        logging.warning(
            "Invalid status '%s' provided for parking lot %i", 
            lot_status, lid
            )
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Bad Request",
                "message": f"Invalid status. Must be one of: {valid_statuses}",
                "code": "INVALID_STATUS",
            },
        )

    if lot_status == "closed":
        if not closed_reason:
            logging.warning(
                "Closed reason required when setting status to closed for parking lot %i",
                lid,
            )
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Bad Request",
                    "message": "closed_reason is required when status is 'closed'",
                    "code": "MISSING_CLOSED_REASON",
                },
            )
        if not closed_date:
            closed_date = date.today()

    updated_lot = ParkingLotCreate(**parking_lot.model_dump())
    updated_lot.status = lot_status
    updated_lot.closed_reason = closed_reason if lot_status == "closed" else None
    updated_lot.closed_date = closed_date if lot_status == "closed" else None

    success = parking_lot_model.update_parking_lot(lid, updated_lot)
    if not success:
        logging.error("Failed to update status for parking lot %i", lid)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal Server Error",
                "message": "Failed to update parking lot status",
                "code": "UPDATE_FAILED",
            },
        )

    logging.info("Successfully updated parking lot %i status to '%s'", lid, lot_status)
    return {
        "message": "Parking lot status updated successfully",
        "parking_lot_id": lid,
        "new_status": lot_status,
        "closed_reason": closed_reason,
        "closed_date": closed_date,
    }

@router.put("/parking-lots/{lid}/reserved")
def update_parking_lot_reserved_count(lid: int, action: str) -> bool:
    """Updates the amount of people that currently have a reservation in a specific parking lot.

    Args:
        lid (int): The id of the parking lot.
        action (str): Whether to increase or decrease the amount of reservations.
    
    Returns:
        boolean: Whether the update was a success or not.
    """
    try:
        parking_lot = get_lot_if_exists(lid)
        parking_lot = ParkingLot(**parking_lot.model_dump())
        if not parking_lot:
            return False

        if action == "increase":
            if parking_lot.reserved >= parking_lot.capacity:
                return False  # Parking lot is vol
            parking_lot.reserved += 1
        elif action == "decrease" and  parking_lot.reserved > 0:
            parking_lot.reserved -= 1

        return parking_lot_model.update_parking_lot_reserved(lid, parking_lot.reserved)
    except Exception as e:
        logging.error(
            "Failed to update reserved count for parking lot %i: %s", lid, str(e)
        )
        return False


# endregion


# region DELETE
@router.delete("/parking-lots/{lid}")
async def delete_parking_lot(
    lid: int,
    _: User = Depends(require_role(UserRole.SUPERADMIN)),
):
    """Deletes a parking lot based on id. Must be logged in as superadmin.

    Args:
        lid (int): The id of the parking lot.
        _ (User): Checks if the logged in user is a super admin.

    Returns:
        dict[str, str]: A confirmation that the parking lot has been deleted.

    Raises:
        HTTPException: Raises 404 if there are no parking lots with the specified id.
        HTTPException: Raises 409 if there are active sessions in this parking lot.
        HTTPException: Raises 500 if there is an error when updateng the parking lot.
        HTTPException: Raises 400 if the provided data is invalid.
        HTTPException: Raises 403 if the logged in user is not a super admin.
        HTTPException: Raises 401 if there is no user logged in.
    """
    # logging.info(
    #     "User with id %i attempting to delete parking lot with id %i",
    #     current_user.id,
    #     lid,
    # )

    # Check if parking lot exists
    logging.debug("Checking if parking lot %i exists", lid)
    _ = get_lot_if_exists(lid)

    # Check if parking lot has active sessions
    logging.debug("Checking for active sessions in parking lot %i", lid)
    sessions = parking_lot_model.get_all_sessions_by_lid(lid)
    active_sessions = [s for s in sessions if s.end_time is None]

    if active_sessions:
        logging.warning(
            "Cannot delete parking lot with id %i - has %i active sessions",
            lid,
            len(active_sessions),
        )
        raise HTTPException(
            status_code=409,
            detail={
                "error": "Conflict",
                "message": "Cannot delete parking lot with active sessions." 
                f" Found {len(active_sessions)} active sessions.",
                "code": "ACTIVE_SESSIONS_EXIST",
            },
        )

    logging.info(
        "No active sessions found, proceeding with deletion of parking lot %i", lid
    )

    # Delete the parking lot
    logging.debug("Attempting to delete parking lot %i from database", lid)
    success = parking_lot_model.delete_parking_lot(lid)

    if not success:
        logging.error("Failed to delete parking lot with id %i from database", lid)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal Server Error",
                "message": "Failed to delete parking lot",
                "code": "DELETE_FAILED",
            },
        )

    logging.info("Successfully deleted parking lot with id %i", lid)
    return {
        "message": "Parking lot deleted successfully",
        "parking_lot_id": lid,
    }


# TODO: delete session by session lid (admin only)  /parking-lots/{lid}/sessions/{sid}
#@router.delete("/parking-lots/{lid}/sessions/{sid}")
#async def delete_parking_session(
#    lid: int,
#    sid: int,
#    current_user: User = Depends(require_lot_access),
#):  # dit is van session zelf
#    pass


# endregion

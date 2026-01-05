"""
This file contains all endpoints related to parking lots.
"""

from datetime import date
from api.models.parking_lot_model import ParkingLotModel
from api.datatypes.parking_lot import Parking_lot, Parking_lot_create
from api.datatypes.user import User, UserRole
from api.auth_utils import get_current_user, require_role
from fastapi import APIRouter, HTTPException, status, Depends

import logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["parking lot"])

parking_lot_model: ParkingLotModel = ParkingLotModel()

def get_lot_if_exists(lid: int):
    """
    Gets a parking lot based on a specific is. if the parking lot cannot be found, it raises a 404 exception.
    @param: lid
    @return: ParkingLot or 404 exception

    """
    parking_lot = parking_lot_model.get_parking_lot_by_lid(lid)
    if parking_lot:
        logger.info("Successfully retrieved parking lot with id %i", lid)
        return parking_lot

    logger.warning("Parking lot with id %i does not exist", lid)
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
    parking_lot_data: Parking_lot_create,
    _: User = Depends(require_role(UserRole.SUPERADMIN)),
):
    """
    Creates a parking lot based on the provided data.
    In order to successfully create a parking lot, the user must be a superadmin.
    @param: parking_lot_data
    @param: current_user
    @return: parking_lot
    """
    # logger.info(
    #     "User with id %i attempting to create a new parking lot", current_user.id
    # )

    logger.debug("Generating new ID for parking lot")
    parking_lots = parking_lot_model.get_all_parking_lots()
    new_id = max([lot.id for lot in parking_lots], default=0) + 1
    logger.debug("Generated new parking lot ID: %i", new_id)

    logger.debug(
        "Creating parking lot object with data: name='%s', location='%s', capacity=%i",
        parking_lot_data.name,
        parking_lot_data.location,
        parking_lot_data.capacity,
    )

    parking_lot = Parking_lot(
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

    logger.info(
        "Creating parking lot with id %i and name '%s' at location '%s'",
        new_id,
        parking_lot.name,
        parking_lot.location,
    )

    try:
        parking_lot_model.create_parking_lot(parking_lot)
        logger.info("Successfully created parking lot with id %i in database", new_id)

    except Exception as e:
        logger.error("Failed to create parking lot in database: %s", str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal Server Error",
                "message": "Failed to create parking lot",
                "code": "CREATE_FAILED",
            },
        )
    return parking_lot


# endregion


# region GET
@router.get("/parking-lots/")
async def get_all_parking_lots():
    """
    Gets all parking lots
    @return: all parking lots
    """
    logger.info("Retrieving all parking lots")
    parking_lots = parking_lot_model.get_all_parking_lots()
    if len(parking_lots) == 0:
        logger.warning("No parking lots found in the system")
        raise HTTPException(
            status_code=204,
            detail={
                "error": "No Content",
                "message": "There are no parking lots",
                "code": "PARKING_LOT_NOT_FOUND",
            },
        )
    logger.info("Successfully retrieved %i parking lots", len(parking_lots))
    return parking_lots


@router.get("/parking-lots/{lid}")
async def get_parking_lot_by_lid(lid: int):
    """
    Gets a single parking lot by id
    @param: lid
    @return: a single parking lot
    """
    return get_lot_if_exists(lid)




@router.get("/parking-lots/{lid}/sessions")
async def get_all_sessions_by_lid(
    lid: int,
    _: User = Depends(require_role(UserRole.SUPERADMIN)),
):
    """
    Gets all sessions for a parking lot by id
    @param: lid
    @return: all sessions of a speccific parking lot
    """
    logger.info("A superadmin is trying to retrieve all sessions of parking lot %i", lid)

    _ = get_lot_if_exists(lid)

    logger.info("A superadmin retrieved all sessions for parking lot %i", lid)
    sessions = parking_lot_model.get_all_sessions_by_lid(lid)
    logger.info(
        "Successfully retrieved %i sessions for parking lot %i",
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
    """
    Gets a single session for a parking lot by id
    @param: lid
    @param: sid
    @return: a single session of a specfic parking lot
    """
    logger.info("A superadmin is trying to receive session %i from parking lot %i", sid, lid)

    _ = get_lot_if_exists(lid)

    logger.info("Retrieving session %i for parking lot %i", sid, lid)
    session = parking_lot_model.get_session_by_lid_and_sid(lid, sid)
    if session:
        logger.info(
            "Successfully retrieved session %i for parking lot %i", sid, lid
        )
        return session

    logger.warning("Session %i does not exist for parking lot %i", sid, lid)
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
    """
    Gets all parking lot based on a location
    @param: location
    @return: all parking lot based of a location
    """
    logger.info(
        "Information about parking lots at location %s are being retrieved",
        location,
    )
    parking_lots = parking_lot_model.find_parking_lots(location=location)

    if len(parking_lots) == 0:
        logger.warning("No parking lots found in location: %s", location)
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Not Found",
                "message": f"No parking lots found in location: {location}",
                "code": "PARKING_LOT_NOT_FOUND",
            },
        )

    logger.info(
        "Successfully retrieved %i parking lots in location: %s",
        len(parking_lots),
        location,
    )
    return parking_lots


# TODO? PO ok maar eerst de rest: get parking lot reservations                /parking-lots/{id}/reservations
# TODO? PO ok maar eerst de rest: get parking lot stats (admin only)          /parking-lots/{id}/stats
# endregion
# endregion


# region PUT
@router.put("/parking-lots/{lid}")
async def update_parking_lot(
    lid: int,
    updated_lot: Parking_lot_create,
    current_user: User = Depends(require_role(UserRole.SUPERADMIN)),
):
    """
    Updeates a parking lot based on values provided by a superadmin.
    to use this endpoint, it must be called by an admin.
    @param: lid
    @param: updated_lot
    """
    logger.info(
        "Superadmin %i attempting to update parking lot %i",
        current_user.id,
        lid,
    )

    logger.debug("Checking if parking lot %i exists", lid)
    parking_lot = get_lot_if_exists(lid)

    if parking_lot.capacity != updated_lot.capacity:
        logger.info(
            "Updating parking lot '%s' (capacity: %i -> %i)",
            parking_lot.name,
            parking_lot.capacity,
            updated_lot.capacity,
        )
    logger.debug("Attempting database update for parking lot %i", lid)

    try:
        success = parking_lot_model.update_parking_lot(lid, updated_lot)
        if not success:
            logger.error(
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

        logger.info("Successfully updated parking lot with id %i", lid)
        return {
            "message": "Parking lot updated successfully",
            "parking_lot_id": lid,
            "updated_lot": updated_lot,
        }

    except Exception as e:
        logger.error("Exception during parking lot %i update: %s", lid, str(e))
        raise HTTPException(status_code=500, detail="Database error occurred")


@router.put("/parking-lots/{lid}/status")
async def update_parking_lot_status(
    lid: int,
    lot_status: str,
    closed_reason: str = None,
    closed_date: date = None,
    _: User = Depends(get_current_user),
    current_user = Depends(require_role(UserRole.SUPERADMIN)),  # Access check only
):
    """
    Updates the status of a parking lot.
    Must be called by a super admin.
    @param: lid
    @param: lot_status
    @param: closed_reason
    @param: closed_date
    """
    logger.info(
        "Superadmin %i attempting to update status of parking lot %i to '%s'",
        current_user.id,
        lid,
        lot_status,
    )

    parking_lot = get_lot_if_exists(lid)

    valid_statuses = ["open", "closed", "deleted", "maintenance", "full"]
    if lot_status not in valid_statuses:
        logger.warning("Invalid status '%s' provided for parking lot %i", lot_status, lid)
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
            logger.warning(
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

    updated_lot = Parking_lot_create(**parking_lot.model_dump())
    updated_lot.status = lot_status
    updated_lot.closed_reason = closed_reason if lot_status == "closed" else None
    updated_lot.closed_date = closed_date if lot_status == "closed" else None

    success = parking_lot_model.update_parking_lot(lid, updated_lot)
    if not success:
        logger.error("Failed to update status for parking lot %i", lid)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal Server Error",
                "message": "Failed to update parking lot status",
                "code": "UPDATE_FAILED",
            },
        )

    logger.info("Successfully updated parking lot %i status to '%s'", lid, lot_status)
    return {
        "message": "Parking lot status updated successfully",
        "parking_lot_id": lid,
        "new_status": lot_status,
        "closed_reason": closed_reason,
        "closed_date": closed_date,
    }

@router.put("/parking-lots/{lid}/reserved")
def update_parking_lot_reserved_count(lid: int, action: str) -> bool:
    """
    Updates the amount of people that currently have a reservation in a specific parking lot.
    @param: lid
    @param: action
    """
    try:
        parking_lot = get_lot_if_exists(lid)
        parking_lot = Parking_lot(**parking_lot.model_dump())
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
        logger.error(
            "Failed to update reserved count for parking lot %i: %s", lid, str(e)
        )
        return False


# endregion


# region DELETE
@router.delete("/parking-lots/{lid}")
async def delete_parking_lot(
    lid: int,
    current_user: User = Depends(require_role(UserRole.SUPERADMIN)),
):
    """
    Deletes a parking lot based on id. must be logged in as superadmin.
    @param: lid
    """
    logger.info(
        "Superadmin %i attempting to delete parking lot %i",
        current_user.id,
        lid,
    )

    # Check if parking lot exists
    logger.debug("Checking if parking lot %i exists", lid)
    _ = get_lot_if_exists(lid)

    # Check if parking lot has active sessions
    logger.debug("Checking for active sessions in parking lot %i", lid)
    sessions = parking_lot_model.get_all_sessions_by_lid(lid)
    active_sessions = [s for s in sessions if s.end_time is None]

    if active_sessions:
        logger.warning(
            "Cannot delete parking lot %i - has %i active sessions",
            lid,
            len(active_sessions),
        )
        raise HTTPException(
            status_code=409,
            detail={
                "error": "Conflict",
                "message": f"Cannot delete parking lot with active sessions. Found {len(active_sessions)} active sessions.",
                "code": "ACTIVE_SESSIONS_EXIST",
            },
        )

    logger.info(
        "No active sessions found, proceeding with deletion of parking lot %i", lid
    )

    # Delete the parking lot
    logger.debug("Attempting to delete parking lot %i from database", lid)
    success = parking_lot_model.delete_parking_lot(lid)

    if not success:
        logger.error("Failed to delete parking lot with id %i from database", lid)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal Server Error",
                "message": "Failed to delete parking lot",
                "code": "DELETE_FAILED",
            },
        )

    logger.info("Successfully deleted parking lot with id %i", lid)
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

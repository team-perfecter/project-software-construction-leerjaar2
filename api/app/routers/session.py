import logging
from datetime import datetime

from api.auth_utils import get_current_user
from api.datatypes.session import Session
from api.datatypes.user import User
from api.storage.parking_lot_storage import Parking_lot_storage
from api.storage.session_storage import Session_storage
from api.storage.vehicle_storage import Vehicle_storage
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

router = APIRouter(tags=["sessions"])

session_storage: Session_storage = Session_storage()
parking_lot_storage: Parking_lot_storage = Parking_lot_storage()
vehicle_storage: Vehicle_storage = Vehicle_storage()


@router.post("/parking-lots/{lid}/sessions/start", status_code=status.HTTP_201_CREATED)
async def start_parking_session(
    lid: int, vehicle_id: int, current_user: User = Depends(get_current_user)
):
    logging.info(
        "User with id %i attempting to start session at parking lot %i",
        current_user.id,
        lid,
    )

    # parking lot check
    parking_lot = parking_lot_storage.get_parking_lot_by_id(lid)
    if not parking_lot:
        logging.warning("Parking lot with id %i does not exist", lid)
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Parking lot not found",
                "message": f"Parking lot with ID {lid} does not exist",
            },
        )

    # vehicle en user check
    vehicle = vehicle_storage.get_one_vehicle(vehicle_id)
    if not vehicle or vehicle["user_id"] != current_user.id:
        if not vehicle:
            logging.warning("Vehicle with id %i does not exist", vehicle_id)
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Vehicle not found",
                    "message": f"Vehicle with ID {vehicle_id} does not exist",
                },
            )
        else:
            logging.warning(
                "User %i tried to start session with vehicle %i that doesn't belong to them",
                current_user.id,
                vehicle_id,
            )
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "Forbidden",
                    "message": "Vehicle does not belong to current user",
                },
            )

    # active session check voor vehicle
    existing_sessions = session_storage.get_all_sessions_by_id(
        parking_lot_id=lid, vehicle_id=vehicle_id, active_only=True
    )

    if existing_sessions:
        logging.warning(
            "Active session already exists for vehicle %i at parking lot %i",
            vehicle_id,
            lid,
        )
        raise HTTPException(
            status_code=409,
            detail={
                "error": "Session already exists",
                "message": f"An active session already exists for this vehicle at this parking lot",
            },
        )

    # create new session
    all_sessions = session_storage.get_sessions()
    new_session_id = max([s.id for s in all_sessions], default=0) + 1

    new_session = Session(
        id=new_session_id,
        parking_lot_id=lid,
        user_id=current_user.id,
        vehicle_id=vehicle_id,
        license_plate=vehicle["license_plate"],
        start_time=datetime.now(),
        end_time=None,
        payment_status="pending",
    )

    # Save session
    session_storage.start_session(new_session)

    logging.info(
        "Successfully started session %i for user %i at parking lot %i with vehicle %i",
        new_session_id,
        current_user.id,
        lid,
        vehicle_id,
    )

    return {
        "message": "Session started successfully",
        "session_id": new_session_id,
        "parking_lot_id": lid,
        "vehicle_id": vehicle_id,
        "license_plate": vehicle["license_plate"],
        "start_time": new_session.start_time.isoformat(),
    }

import logging
from datetime import datetime

from api.auth_utils import get_current_user
from api.datatypes.session import Session, SessionCreate
from api.datatypes.user import User
from api.models.parking_lot_model import ParkingLotModel
from api.models.session_model import SessionModel
from fastapi import APIRouter, Depends, HTTPException, status

from api.models.vehicle_model import Vehicle_model

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

router = APIRouter(tags=["sessions"])

session_storage: SessionModel = SessionModel()
parking_lot_model: ParkingLotModel = ParkingLotModel()
vehicle_model: Vehicle_model = Vehicle_model()


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
    parking_lot = parking_lot_model.get_parking_lot_by_id(lid)
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
    vehicle = vehicle_model.get_one_vehicle(vehicle_id)
    if not vehicle or vehicle.user_id != current_user.id:
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
    existing_sessions =  False #session_storage.get_all_sessions_by_id(lid, vehicle_id)

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

    # Save session
    session = session_storage.create_session(lid, current_user.id, vehicle_id)
    if session is None:
        return "This vehicle already has a session"

    logging.info(
        "Successfully started session for user %i at parking lot %i with vehicle %i",
        current_user.id,
        lid,
        vehicle_id,
    )

    return {
        "message": "Session started successfully",
        "parking_lot_id": lid,
        "vehicle_id": vehicle_id,
        "license_plate": vehicle.license_plate,
    }

@router.post("/parking-lots/{lid}/sessions/stop")
async def stop_parking_session(vehicle_id: int, current_user: User = Depends(get_current_user)):
    active_sessions = session_storage.get_vehicle_sessions(vehicle_id)
    print(active_sessions)
    if not active_sessions:
        return "This vehicle has no active sessions"
    session_storage.stop_session(active_sessions)
    return "Session stopped successfully"

"""
This file contains all endpoints related to sessions.
"""

import logging
from starlette.responses import JSONResponse
from fastapi import APIRouter, Depends, HTTPException, status
from api.auth_utils import get_current_user
from api.datatypes.payment import PaymentCreate
from api.datatypes.user import User
from api.models.parking_lot_model import ParkingLotModel
from api.models.payment_model import PaymentModel
from api.models.session_model import SessionModel
from api.models.vehicle_model import VehicleModel

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

router = APIRouter(tags=["sessions"])

session_model: SessionModel = SessionModel()
parking_lot_model: ParkingLotModel = ParkingLotModel()
vehicle_model: VehicleModel = VehicleModel()
payment_model: PaymentModel = PaymentModel()


@router.post("/parking-lots/{lid}/sessions/start", status_code=status.HTTP_201_CREATED)
async def start_parking_session(
    lid: int,
    vehicle_id: int,
    current_user: User = Depends(get_current_user)
):
    """Starts a session on a specified parking lot.

    Args:
        lid (int): The parking lot of the session.
        vehicle_id (int): The vehicle that started the session.
        current_user (User): The logged in user.
    
    Returns:
        dict[str, str]: Confirmation that the session was created successfully.

    Raises:
        HTTPException: Raises 404 if the vehicle or parking lot does not exist.
        HTTPException: Raises 403 if the vhicle does not belong to the logged in user.
        HTTPException: Raises 409 if this vehicle already has a session.
    """
    logging.info(
        "User with id %i attempting to start session at parking lot %i",
        current_user.id,
        lid,
    )

    # parking lot check
    parking_lot = parking_lot_model.get_parking_lot_by_lid(lid)
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
                "message": "An active session already exists for this vehicle at this parking lot",
            },
        )

    # create new session

    # Save session
    session = session_model.create_session(lid, current_user.id, vehicle_id)
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
        "license_plate": vehicle["license_plate"],
    }

@router.post("/parking-lots/{lid}/sessions/stop")
async def stop_parking_session(vehicle_id: int,
                               current_user: User = Depends(get_current_user)):
    """stops a session on a specified parking lot.

    Args:
        lid (int): The parking lot of the session.
        vehicle_id (int): The id of the vehicle.
        current_user (User): The logged in user.
    
    Returns:
        str: Confirmation whether the session was stopped successfully.
    """
    active_sessions = session_model.get_vehicle_sessions(vehicle_id)
    if not active_sessions:
        return "This vehicle has no active sessions"
    session = session_model.stop_session(active_sessions)
    payment: PaymentCreate = PaymentCreate(
        user_id=current_user.id,
        amount = session["cost"]
    )
    payment_model.create_payment(payment)
    return "Session stopped successfully"

@router.get("/sessions/active")
async def get_active_sessions():
    """Retrieves all sessions.
    
    Returns:
        dict[str, [Session]]: Information of all the sessions.
    """
    sessions = session_model.get_active_sessions()
    return {"active_sessions": sessions}

@router.get("/sessions/vehicle/{vehicle_id}")
async def get_sessions_vehicle(vehicle_id: int,
                               user: User = Depends(get_current_user)):
    """Retrieves the sessions of the specified vehicle.

    Args:
        vehicle_id (int): The vehicle that started the session.
        current_user (User): The logged in user.
    
    Returns:
        JSONResponse: A list of the sessions of a vehicle.

    Raises:
        HTTPException: Raises 404 if the vehicle does not exist.
    """
    vehicle = vehicle_model.get_one_vehicle(vehicle_id)
    if not vehicle or vehicle["user_id"] != user.id:
        raise HTTPException(status_code=404,
                            detail={"error": "Vehicle not found", 
                                    "message": f"Vehicle with ID {vehicle_id} does not exist"
                                    })
    sessions = session_model.get_vehicle_sessions(vehicle_id)
    return JSONResponse(content={"message": sessions}, status_code=201)

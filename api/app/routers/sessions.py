from api.auth_utils import get_current_user
from api.datatypes.payment import PaymentCreate
from api.datatypes.user import User
from api.models.parking_lot_model import ParkingLotModel
from api.models.payment_model import PaymentModel
from api.models.session_model import SessionModel
from fastapi import APIRouter, Depends, HTTPException, status
from starlette.responses import JSONResponse
from api.models.vehicle_model import Vehicle_model

import logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["sessions"])

session_model: SessionModel = SessionModel()
parking_lot_model: ParkingLotModel = ParkingLotModel()
vehicle_model: Vehicle_model = Vehicle_model()
payment_model: PaymentModel = PaymentModel()


@router.post("/parking-lots/{lid}/sessions/start", status_code=status.HTTP_201_CREATED)
async def start_parking_session(
    lid: int, vehicle_id: int, current_user: User = Depends(get_current_user)
):
    logger.info(
        "User %i attempting to start session at parking lot %i",
        current_user.id,
        lid,
    )

    # parking lot check
    parking_lot = parking_lot_model.get_parking_lot_by_lid(lid)
    if not parking_lot:
        logger.warning("Parking lot %i does not exist", lid)
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Parking lot not found",
                "message": f"Parking lot {lid} does not exist",
            },
        )

    # vehicle en user check
    vehicle = vehicle_model.get_one_vehicle(vehicle_id)
    if not vehicle or vehicle["user_id"] != current_user.id:
        if not vehicle:
            logger.warning("Vehicle with id %i does not exist", vehicle_id)
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Vehicle not found",
                    "message": f"Vehicle with ID {vehicle_id} does not exist",
                },
            )
        else:
            logger.warning(
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
        logger.warning(
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
    session = session_model.create_session(lid, current_user.id, vehicle_id)
    if session is None:
        logger.warning("Vehcile %i already has a session", vehicle_id)
        return JSONResponse(content={"message": "This vehicle already has a session"}, status_code=209)
    
    logger.info(
        "Successfully started session for user %i at parking lot %i with vehicle %i",
        current_user.id,
        lid,
        vehicle_id,
    )
    return JSONResponse(content= {
        "message": "Session started successfully",
        "parking_lot_id": lid,
        "vehicle_id": vehicle_id,
        "license_plate": vehicle["license_plate"],
    }, status_code=201)

@router.post("/parking-lots/{lid}/sessions/stop")
async def stop_parking_session(vehicle_id: int, current_user: User = Depends(get_current_user)):
    logger.info("user %i tried to stop a session of vehicle %i", current_user.id, vehicle_id)
    active_sessions = session_model.get_vehicle_sessions(vehicle_id)
    if not active_sessions:
        logger.warning("User %i tried to stop the session of vehicle %i, but this vehicle has no session", current_user.id, vehicle_id)
        return JSONResponse(
            content= {"message": "This vehicle has no active sessions"}, 
            status_code=404
            )

    session = session_model.stop_session(active_sessions)

    payment: PaymentCreate = PaymentCreate(
        user_id=current_user.id,
        amount = session["cost"]
    )
    payment_model.create_payment(payment)
    logger.info("Session of vehicle %i successfully stopped", vehicle_id)
    return JSONResponse(
        content= {"message": "Session stopped successfully"}, 
        status_code=201
        )

@router.get("/sessions/active")
async def get_active_sessions():
    """
    Geeft een lijst van alle actieve sessies.
    """
    sessions = session_model.get_active_sessions()
    return {"active_sessions": sessions}

@router.get("/sessions/vehicle/{vehicle_id}")
async def get_sessions_vehicle(vehicle_id: int, user: User = Depends(get_current_user)):
    logger.info("User %i tried to retrieve the session of vehicle %i", user.id, vehicle_id)
    vehicle = vehicle_model.get_one_vehicle(vehicle_id)
    if not vehicle or vehicle["user_id"] != user.id:
        logger.warning("Vehicle %i could not be found", vehicle_id)
        raise HTTPException(status_code=404, detail={"error": "Vehicle not found", "message": f"Vehicle with ID {vehicle_id} does not exist"})
    sessions = session_model.get_vehicle_sessions(vehicle_id)
    print(sessions)
    logger.info("Session for vehicle %i found", vehicle_id)
    return sessions

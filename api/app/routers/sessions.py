import logging
from datetime import datetime

from api.auth_utils import get_current_user
from api.datatypes.payment import PaymentCreate
from api.datatypes.user import User
from api.models.parking_lot_model import ParkingLotModel
from api.models.payment_model import PaymentModel
from api.models.session_model import SessionModel
from fastapi import APIRouter, Depends, HTTPException, status
from starlette.responses import JSONResponse
from api.models.vehicle_model import Vehicle_model
from api.models.reservation_model import Reservation_model
from api.session_calculator import generate_payment_hash, generate_transaction_validation_hash, calculate_price

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

router = APIRouter(tags=["sessions"])

session_model: SessionModel = SessionModel()
parking_lot_model: ParkingLotModel = ParkingLotModel()
vehicle_model: Vehicle_model = Vehicle_model()
payment_model: PaymentModel = PaymentModel()
reservation_model: Reservation_model = Reservation_model()


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
    print("CHECK 1")
    print(vehicle)
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
                "message": f"An active session already exists for this vehicle at this parking lot",
            },
        )

    # create new session

    # Save session
    session = session_model.create_session(lid, current_user.id, vehicle_id, None)
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
async def stop_parking_session(
    lid: int,
    vehicle_id: int,
    current_user: User = Depends(get_current_user)
):
    session = session_model.get_vehicle_session(vehicle_id)
    if not session:
        return "This vehicle has no active sessions"
    
    if getattr(session, "reservation_id", None) is not None:
        raise HTTPException(
            status_code=403,
            detail="Cannot stop a session that was started from a reservation via this endpoint."
        )

    parking_lot = parking_lot_model.get_parking_lot_by_lid(session.parking_lot_id)
    cost = calculate_price(parking_lot, session)

    session = session_model.stop_session(session, cost)

    vehicle = vehicle_model.get_one_vehicle(vehicle_id)
    transaction = generate_payment_hash(str(session.id), vehicle["license_plate"])
    payment_hash = generate_transaction_validation_hash()
    payment = PaymentCreate(
        user_id=current_user.id,
        amount=cost,
        transaction=transaction,
        hash=payment_hash,
        session_id=session.id
    )
    payment_model.create_payment(payment)
    return "Session stopped successfully"

@router.get("/sessions/active")
async def get_active_sessions():
    """
    Geeft een lijst van alle actieve sessies.
    """
    sessions = session_model.get_active_sessions()
    return {"active_sessions": sessions}

@router.get("/sessions/vehicle/{vehicle_id}")
async def get_sessions_vehicle(vehicle_id: int, user: User = Depends(get_current_user)):
    vehicle = vehicle_model.get_one_vehicle(vehicle_id)
    if not vehicle or vehicle["user_id"] != user.id:
        raise HTTPException(status_code=404, detail={"error": "Vehicle not found", "message": f"Vehicle with ID {vehicle_id} does not exist"})
    sessions = session_model.get_vehicle_sessions(vehicle_id)
    print(sessions)
    return JSONResponse(content={"message": sessions}, status_code=201)


@router.post("/sessions/start-from-reservation/{reservation_id}")
async def start_session_from_reservation(
    reservation_id: int,
    current_user: User = Depends(get_current_user)
):
    # Get reservation
    reservation = reservation_model.get_reservation_by_id(reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    if reservation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Reservation does not belong to current user")

    # Check if session already exists for this vehicle and parking lot
    existing_session = session_model.get_vehicle_session(reservation.vehicle_id)
    if existing_session and existing_session.parking_lot_id == reservation.parking_lot_id:
        raise HTTPException(status_code=409, detail="Session already exists for this reservation")

    # Start session
    session = session_model.create_session(
        reservation.parking_lot_id,
        reservation.user_id,
        reservation.vehicle_id,
        reservation.id
    )
    if not session:
        raise HTTPException(status_code=500, detail="Failed to start session")

    return {"message": "Session started", "session": session}

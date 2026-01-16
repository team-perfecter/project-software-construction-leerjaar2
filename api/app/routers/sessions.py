import logging
from datetime import datetime, timedelta

from api.auth_utils import get_current_user, get_current_user_optional
from api.datatypes.payment import PaymentCreate, PaymentUpdate
from api.datatypes.user import User
from api.models.parking_lot_model import ParkingLotModel
from api.models.payment_model import PaymentModel
from api.models.session_model import SessionModel
from fastapi import APIRouter, Depends, HTTPException, status
from starlette.responses import JSONResponse
from api.models.vehicle_model import Vehicle_model
from api.models.reservation_model import Reservation_model
from api.session_calculator import generate_payment_hash, generate_transaction_validation_hash, calculate_price

import logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["sessions"])

session_model: SessionModel = SessionModel()
parking_lot_model: ParkingLotModel = ParkingLotModel()
vehicle_model: Vehicle_model = Vehicle_model()
payment_model: PaymentModel = PaymentModel()
reservation_model: Reservation_model = Reservation_model()


@router.post("/parking-lots/{lid}/sessions/start/{license_plate}", status_code=status.HTTP_201_CREATED)
async def start_parking_session(
    lid: int, license_plate: str, current_user: User | None = Depends(get_current_user_optional),
):
    user_id = current_user.id if current_user else None
    
    logger.info(
        "User %i attempting to start session at parking lot %i",
        user_id,
        lid,
    )

    # parking lot check
    parking_lot = parking_lot_model.get_parking_lot_by_lid(lid)
    if not parking_lot:
        logger.warning("Parking lot %i does not exist", lid)
        raise HTTPException(status_code=404, detail={"error": "Parking lot not found", "message": f"Parking lot {lid} does not exist",})

    # active session check voor vehicle
    existing_session = session_model.get_vehicle_session(license_plate)

    if existing_session:
        logger.warning(
            "Active session already exists for vehicle %i at parking lot %i",
            license_plate,
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
    logger.warning("user: %i freiofjewpogoewpogkewpo;gewgoejioeriiubher work", user_id)

    # Save session
    session = session_model.create_session(lid, user_id, license_plate, None)
    if session is None:
        logger.warning("Vehcile %i already has a session", license_plate)
        return JSONResponse(content={"message": "This vehicle already has a session"}, status_code=209)
    
    logger.info(
        "Successfully started session for user %i at parking lot %i with vehicle %i",
        user_id,
        lid,
        license_plate,
    )
    return JSONResponse(content= {
        "message": "Session started successfully",
        "parking_lot_id": lid,
        "license_plate": license_plate,
    }, status_code=201)

@router.post("/parking-lots/{lid}/sessions/stop/{license_plate}")
async def stop_parking_session(
    lid: int,
    license_plate: str,
    current_user: User = Depends(get_current_user_optional)
):
    user_id = current_user.id if current_user else None
    session = session_model.get_vehicle_session(license_plate)
    if not session:
        return "This vehicle has no active session"
    
    if getattr(session, "reservation_id", None) is not None:
        raise HTTPException(
            status_code=403,
            detail="Cannot stop a session that was started from a reservation via this endpoint."
        )

    parking_lot = parking_lot_model.get_parking_lot_by_lid(session.parking_lot_id)
    cost = calculate_price(parking_lot, session, None)

    session = session_model.stop_session(session, cost)

    transaction = generate_payment_hash(str(session.id), license_plate)
    payment_hash = generate_transaction_validation_hash()
    payment = PaymentCreate(
        user_id=user_id,
        amount=cost,
        transaction=transaction,
        hash=payment_hash,
        session_id=session.id
    )
    payment_model.create_payment(payment)
    logger.info("Session of vehicle %i successfully stopped", license_plate)
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
    logger.info("User %s tried to retrieve the session of vehicle %s", user.id, vehicle_id)
    vehicle = vehicle_model.get_one_vehicle(vehicle_id)
    if not vehicle or vehicle["user_id"] != user.id:
        logger.warning("Vehicle %s could not be found", vehicle_id)
        raise HTTPException(status_code=404, detail={"error": "Vehicle not found", "message": f"Vehicle with ID {vehicle_id} does not exist"})
    sessions = session_model.get_vehicle_sessions(vehicle_id)
    print(sessions)
    return JSONResponse(content={"message": sessions}, status_code=201)


@router.post("/sessions/reservations/{reservation_id}/start")
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


@router.post("/sessions/reservations/{reservation_id}/stop")
async def stop_session_from_reservation(
    reservation_id: int,
    current_user: User = Depends(get_current_user)
):
    session = session_model.get_session_by_reservation_id(reservation_id)
    if not session:
        raise HTTPException(status_code=404, detail="No active session found for this reservation")
    if session.stopped is not None:
        raise HTTPException(status_code=409, detail="Session already stopped")

    reservation = reservation_model.get_reservation_by_id(reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    parking_lot = parking_lot_model.get_parking_lot_by_lid(session.parking_lot_id)
    session = session_model.stop_session(session, calculate_price(parking_lot, session))

    # Only create/update payment if the driver overstayed
    if session.stopped > reservation.end_time:
        overtime_start = reservation.end_time
        overtime_end = session.stopped
        overtime_session = session
        overtime_session.started = overtime_start
        overtime_session.stopped = overtime_end
        extra_cost = calculate_price(parking_lot, overtime_session)

        # Find the original payment for this reservation
        original_payment = payment_model.get_payment_by_reservation_id(reservation_id)
        if not original_payment:
            raise HTTPException(status_code=404, detail="Original payment not found")

        if not original_payment["completed"]:
            # Add extra cost to the original payment
            updated_payment = PaymentUpdate(
                amount=original_payment["amount"] + extra_cost)
            update_fields = updated_payment.dict(exclude_unset=True)
            payment_model.update_payment(original_payment["id"], update_fields)
            return {
                "message": "Reservation session stopped. Extra cost added to original payment=.",
                "session": session,
                "updated_payment": updated_payment.amount
            }
        else:
            # Create a new payment for the extra cost
            vehicle = vehicle_model.get_one_vehicle(session.vehicle_id)
            transaction = generate_payment_hash(str(session.id), vehicle["license_plate"])
            payment_hash = generate_transaction_validation_hash()
            payment = PaymentCreate(
                user_id=current_user.id,
                amount=extra_cost,
                transaction=transaction,
                hash=payment_hash,
                session_id=session.id,
                reservation_id=reservation_id
            )
            payment_model.create_payment(payment)
            return {
                "message": "Reservation session stopped. Extra payment created for overtime.",
                "session": session,
                "extra_payment": payment.amount
            }

    return {
        "message": "Reservation session stopped successfully. No extra cost added.",
        "session": session
    }

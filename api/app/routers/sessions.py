"""
This file contains all endpoints related to sessions.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from api.auth_utils import get_current_user
from api.datatypes.payment import PaymentCreate, PaymentUpdate
from api.datatypes.user import User
from api.models.parking_lot_model import ParkingLotModel
from api.models.payment_model import PaymentModel
from api.models.session_model import SessionModel
from api.models.vehicle_model import VehicleModel
from api.models.reservation_model import ReservationModel
from api.session_calculator import (calculate_price,
                                    generate_payment_hash,
                                    generate_transaction_validation_hash)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["sessions"])

session_model: SessionModel = SessionModel()
parking_lot_model: ParkingLotModel = ParkingLotModel()
vehicle_model: VehicleModel = VehicleModel()
payment_model: PaymentModel = PaymentModel()
reservation_model: ReservationModel = ReservationModel()


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
                "message": "An active session already exists for this vehicle at this parking lot",
            },
        )

    # create new session

    # Save session
    session = session_model.create_session(lid, current_user.id, vehicle_id, None)
    if session is None:
        logger.warning("Vehcile %i already has a session", vehicle_id)
        return JSONResponse(content={
                            "message": "This vehicle already has a session"}, 
                            status_code=209)

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
async def stop_parking_session(
    vehicle_id: int,
    current_user: User = Depends(get_current_user)
):
    """stops a session on a specified parking lot.

    Args:
        vehicle_id (int): The id of the vehicle.
        current_user (User): The logged in user.
    
    Returns:
        str: Confirmation whether the session was stopped successfully.
    """
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
    payment: PaymentCreate = PaymentCreate(
        user_id=current_user.id,
        amount=cost,
        transaction=transaction,
        hash=payment_hash,
        session_id=session.id
    )
    payment_model.create_payment(payment)
    logger.info("Session of vehicle %i successfully stopped", vehicle_id)
    return JSONResponse(
        content= {"message": "Session stopped successfully"},
        status_code=201
        )

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
    logger.info("User %i tried to retrieve the session of vehicle %i", user.id, vehicle_id)
    vehicle = vehicle_model.get_one_vehicle(vehicle_id)
    if not vehicle or vehicle["user_id"] != user.id:
        logger.warning("Vehicle %i could not be found", vehicle_id)
        raise HTTPException(status_code=404,
                            detail={"error": "Vehicle not found", 
                                    "message": f"Vehicle with ID {vehicle_id} does not exist"
                                    })
    sessions = session_model.get_vehicle_sessions(vehicle_id)
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

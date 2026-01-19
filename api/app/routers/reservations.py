"""
This file contains all endpoints related to reservations.
"""

import logging
from datetime import datetime
from fastapi import Depends, APIRouter, HTTPException
from api.auth_utils import get_current_user
from api.datatypes.user import User
from api.datatypes.payment import PaymentCreate
from api.datatypes.reservation import Reservation, ReservationCreate
from api.models.parking_lot_model import ParkingLotModel
from api.models.reservation_model import ReservationModel
from api.models.discount_code_model import DiscountCodeModel
from api.models.vehicle_model import VehicleModel
from api.models.session_model import SessionModel
from api.models.payment_model import PaymentModel
from api.session_calculator import generate_payment_hash, generate_transaction_validation_hash, calculate_price
from api.utilities.discount_code_validation import use_discount_code_validation


logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["reservations"]
)

reservation_model: ReservationModel = ReservationModel()
parking_lot_model: ParkingLotModel = ParkingLotModel()
vehicle_model: VehicleModel = VehicleModel()
session_model: SessionModel = SessionModel()
payment_model: PaymentModel = PaymentModel()
discount_code_model: DiscountCodeModel = DiscountCodeModel()


@router.get("/reservations/vehicle/{vehicle_id}")
async def reservations(vehicle_id: int, current_user: User = Depends(get_current_user)):
    vehicle = vehicle_model.get_one_vehicle(vehicle_id)
    if vehicle is None:
        logger.warning("Vehicle %s not found", vehicle_id)
        raise HTTPException(status_code=404, detail="Vehicle not found")

    if vehicle["user_id"] != current_user.id:
        raise HTTPException(
            status_code=403, detail="This vehicle does not belong to the logged in user")

    reservation_list: list[Reservation] = reservation_model.get_reservations_by_vehicle(
        vehicle_id)
    return reservation_list


@router.post("/reservations/create")
async def create_reservation(
    reservation: ReservationCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new reservation for a vehicle at a specific parking lot.

    Args:
        reservation (ReservationCreate): The reservation data.
        user (User): The currently authenticated user (injected via dependency).

    Raises:
        HTTPException: 404 if the parking lot or vehicle does not exist.
        HTTPException: 401 if the date overlaps with another reservation for the same vehicle.
        HTTPException: 403 if the start date is earlier than the current date.
        HTTPException: 403 if the start_date >= end_date

    Returns:
        dict: Confirmation message indicating the reservation was successfully created.
    """
    # Check if parking lot exists
    parking_lot = parking_lot_model.get_parking_lot_by_lid(reservation.parking_lot_id)
    if parking_lot is None:
        logger.warning("Parking lot %s does not exist", reservation.parking_lot_id)
        raise HTTPException(status_code=404, detail={"message": "Parking lot does not exist"})

    # Check if vehicle exists
    vehicle = vehicle_model.get_one_vehicle(reservation.vehicle_id)
    if vehicle == None:
        logger.warning("Vehicle %s does not exist", reservation.vehicle_id)
        raise HTTPException(status_code=404, detail={"message": "Vehicle does not exist"})

    # Check for overlapping reservations for this vehicle
    vehicle_reservations = reservation_model.get_reservations_by_vehicle(reservation.vehicle_id)
    for r in vehicle_reservations:
        if (
            reservation.start_time < r["end_time"] and
            reservation.end_time > r["start_time"]
        ):
            logger.warning(
                "User %s tried to create overlapping reservation for vehicle %s",
                current_user.id, reservation.vehicle_id
            )
            raise HTTPException(
                status_code=409,
                detail={"message": "Requested date has an overlap with another reservation for this vehicle"}
            )

    # Validate start and end times
    
    now = datetime.now()
    if reservation.start_time < now:
        logger.warning(
            "User %s tried to create reservation with start_time in the past: %s",
            current_user.id, reservation.start_time
        )
        raise HTTPException(
            status_code=400,
            detail={"message": f"Invalid start date. The start date cannot be earlier than the current date. current date: {now}, received date: {reservation.start_time}"}
        )
    if reservation.start_time >= reservation.end_time:
        logger.warning(
            "User %s tried to create reservation with start_time >= end_time: %s >= %s",
            current_user.id, reservation.start_time, reservation.end_time
        )
        raise HTTPException(
            status_code=400,
            detail={"message": f"Invalid start date. The start date cannot be later than or equal to the end date. start date: {reservation.start_time}, end date: {reservation.end_time}"}
        )

    # Discount code validation
    discount_code = None
    if reservation.discount_code:
        discount_code = discount_code_model.get_discount_code_by_code(reservation.discount_code)
        if not discount_code:
            logger.error(
                "User ID %s tried to use discount code %s, but it was not found",
                current_user.id, reservation.discount_code
            )
            raise HTTPException(status_code=404, detail="No discount code was found.")
        use_discount_code_validation(discount_code, reservation, current_user, parking_lot)

    # Calculate cost
    cost = calculate_price(parking_lot, reservation, discount_code)

    # Create reservation
    reservation.user_id = current_user.id
    reservation.cost = cost
    reservation_id = reservation_model.create_reservation(reservation)
    logger.info(
        "User %s created reservation %s for vehicle %s at parking lot %s",
        current_user.id, reservation_id, reservation.vehicle_id, reservation.parking_lot_id
    )

    transaction = generate_payment_hash(
        str(reservation_id), vehicle["license_plate"])
    payment_hash = generate_transaction_validation_hash()
    payment = PaymentCreate(
        parking_lot_id=reservation.parking_lot_id,
        user_id=current_user.id,
        amount=cost,
        transaction=transaction,
        hash=payment_hash,
        reservation_id=reservation_id
    )
    payment_model.create_payment(payment)
    logger.info(
        "Payment created for reservation %s by user %s", reservation_id, current_user.id
    )

    return {"message": "Reservation created successfully"}


@router.delete("/reservations/delete/{reservation_id}")
async def delete_reservation(reservation_id: int, current_user: User = Depends(get_current_user)):
    # Controleer of de reservatie bestaat
    reservation: Reservation | None = reservation_model.get_reservation_by_id(
        reservation_id)
    if reservation is None:
        logging.warning("User with id %s tried to delete a reservation that does not exist: %s",
                        current_user.id, reservation_id)
        raise HTTPException(status_code=404, detail={
                            "message": "Reservation not found"})

    # Controleer of de reservatie toebehoort aan de ingelogde gebruiker
    if reservation.user_id != current_user.id:
        logging.warning("User with id %s tried to delete a reservation that does not belong to them: %s",
                        current_user.id, reservation_id)
        raise HTTPException(status_code=403, detail={
                            "message": "This reservation does not belong to the logged-in user"})

    # Verwijder de reservatie
    success = reservation_model.delete_reservation(reservation_id)
    if not success:
        logging.error("Failed to delete reservation with id %s for user %s",
                      reservation_id, current_user.id)
        raise HTTPException(status_code=500, detail={
                            "message": "Failed to delete reservation"})

    logging.info("User with id %s successfully deleted reservation with id %s",
                 current_user.id, reservation_id)
    raise HTTPException(
        detail={"message": "Reservation deleted successfully"}, status_code=200)

"""
This file contains all endpoints related to reservations.
"""

import logging
from fastapi import Depends, APIRouter, HTTPException
from api.auth_utils import get_current_user
from api.datatypes.user import User
from api.datatypes.payment import PaymentCreate
from api.datatypes.reservation import Reservation, ReservationCreate
from api.models.parking_lot_model import ParkingLotModel
from api.models.reservation_model import ReservationModel
from api.models.vehicle_model import VehicleModel
from api.models.session_model import SessionModel
from api.models.payment_model import PaymentModel
from api.session_calculator import (generate_payment_hash,
                                    generate_transaction_validation_hash,
                                    calculate_price)

logger = logging.getLogger(__name__)


router = APIRouter(
    tags=["reservations"]
)

reservation_model: ReservationModel = ReservationModel()
parking_lot_model: ParkingLotModel = ParkingLotModel()
vehicle_model: VehicleModel = VehicleModel()
session_model: SessionModel = SessionModel()
payment_model: PaymentModel = PaymentModel()

@router.get("/reservations/vehicle/{vehicle_id}")
async def vehicle_reservations(vehicle_id: int, user: User = Depends(get_current_user)):
    """
    Retrieve all reservations for a specific vehicle owned by the logged-in user.

    Args:
        vehicle_id (int): The ID of the vehicle for which to fetch reservations.
        user (User): The currently authenticated user (injected via dependency).

    Raises:
        HTTPException: 404 if the vehicle does not exist.
        HTTPException: 403 if the vehicle does not belong to the logged-in user.

    Returns:
        list[Reservation]: A list of reservations associated with the vehicle.
    """

    vehicle = vehicle_model.get_one_vehicle(vehicle_id)
    if vehicle is None:
        raise HTTPException(
            status_code=404,
            detail="Vehicle not found"
        )

    if vehicle["user_id"] != user.id:
        raise HTTPException(
            status_code=403,
            detail="This vehicle does not belong to the logged in user"
        )

    reservation_list: list[Reservation] = reservation_model.get_reservations_by_vehicle(vehicle_id)
    return reservation_list

@router.post("/reservations/create")
async def create_reservation(reservation: ReservationCreate, 
                             current_user: User = Depends(get_current_user)):
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
    parking_lot = parking_lot_model.get_parking_lot_by_lid(reservation.parking_lot_id)
    if parking_lot is None:
        logger.warning("Parking lot %i does not exist", reservation.parking_lot_id)
        raise HTTPException(status_code = 404, detail = {"message": "Parking lot does not exist"})
    
    vehicle = vehicle_model.get_one_vehicle(reservation.vehicle_id)
    if vehicle is None:
        logger.warning("Vehicle %i does not exist", reservation.vehicle_id)
        raise HTTPException(status_code = 404, detail = {"message": "Vehicle does not exist"})
    ### deze error handling werkt niet eens!!!
    # conflicting_time: bool = False
    # vehicle_reservations: list[Reservation] = reservation_model.get_reservation_by_vehicle(vehicle["id"])
    # for reservation in vehicle_reservations:
    #     if reservation["start_date"] < reservation["end_date"] and reservation["end_date"] > reservation["start_date"]:
    #         conflicting_time = True
    #         break
    # if conflicting_time:
    #     raise HTTPException(status_code = 401, detail = {"message": f"Requested date has an overlap with another reservation for this vehicle"})

    # # check if start date is later than the current date
    # if reservation.start_date < datetime.now():
    #     raise HTTPException(status_code = 403, detail = {"message": f"invalid start date. The start date cannot be earlier than the current date. current date: {datetime.now()}, received date: {reservation.start_date}"})

    # # check if the end date is later than the start date
    # if reservation.start_date >= reservation.end_date:
    #     raise HTTPException(status_code = 403, detail = {"message": f"invalid start date. The start date cannot be later than the end date start date: {reservation.start_date}, end date: {reservation.end_date}"})

    #create a new reservation
    parking_lot = parking_lot_model.get_parking_lot_by_lid(reservation.parking_lot_id)
    #errorhandling etc.

    cost = calculate_price(parking_lot, reservation)
    reservation.user_id = current_user.id
    reservation.cost = cost
    reservation_id = reservation_model.create_reservation(reservation)
    #errorhandling etc.

    transaction = generate_payment_hash(str(reservation_id), vehicle["license_plate"])
    payment_hash = generate_transaction_validation_hash()
    payment = PaymentCreate(
        user_id=current_user.id,
        amount=cost,
        transaction=transaction,
        hash=payment_hash,
        reservation_id=reservation_id
    )
    payment_model.create_payment(payment)
    #add error handling for payment

    return {"message": "Reservation created successfully"}

@router.delete("/reservations/delete/{reservation_id}")
async def delete_reservation(reservation_id: int, current_user: User = Depends(get_current_user)):
    """
    Delete a reservation belonging to the logged-in user.

    Args:
        reservation_id (int): The ID of the reservation to delete.
        user (User): The currently authenticated user (injected via dependency).

    Raises:
        HTTPException: 404 if the reservation does not exist.
        HTTPException: 403 if the reservation does not belong to the logged-in user.
        HTTPException: 500 if deletion fails due to a database error.

    Returns:
        dict: Confirmation message indicating the reservation was successfully deleted.
    """
    # Controleer of de reservatie bestaat
    reservation: Reservation | None = reservation_model.get_reservation_by_id(reservation_id)
    if reservation is None:
        logger.warning("User with id %i tried to delete a reservation that does not exist: %i",
                       current_user.id, reservation_id)
        raise HTTPException(status_code=404, detail={"message": "Reservation not found"})

    # Controleer of de reservatie toebehoort aan de ingelogde gebruiker
    if reservation.user_id != current_user.id:
        logger.warning(
            "User with id %i tried to delete a reservation that does not belong to them: %i",
                        current_user.id, reservation_id)
        raise HTTPException(
            status_code=403,
            detail={"message": "This reservation does not belong to the logged-in user"}
        )

    # Verwijder de reservatie
    success = reservation_model.delete_reservation(reservation_id)
    if not success:
        logger.error(
            "Failed to delete reservation with id %i for user %i",
            reservation_id, current_user.id
            )
        raise HTTPException(status_code=500, detail={"message": "Failed to delete reservation"})

    logger.info(
        "User with id %i successfully deleted reservation with id %i",
        current_user.id, reservation_id
        )
    raise HTTPException(detail={"message": "Reservation deleted successfully"}, status_code=200)

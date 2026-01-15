from datetime import datetime
from api.auth_utils import get_current_user
from api.datatypes.user import User
from api.datatypes.payment import PaymentCreate
from fastapi import Depends, APIRouter, HTTPException, status, Body
from api.datatypes.reservation import Reservation, ReservationCreate
from api.datatypes.vehicle import Vehicle
from api.models.parking_lot_model import ParkingLotModel
from api.models.reservation_model import Reservation_model
from api.models.discount_code_model import DiscountCodeModel
from api.models.vehicle_model import Vehicle_model
from api.models.session_model import SessionModel
from api.models.payment_model import PaymentModel
from api.session_calculator import generate_payment_hash, generate_transaction_validation_hash, calculate_price
from api.utilities.discount_code_validation import use_discount_code_validation


import logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["reservations"])

reservation_model: Reservation_model = Reservation_model()
parking_lot_model: ParkingLotModel = ParkingLotModel()
vehicle_model: Vehicle_model = Vehicle_model()
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
        raise HTTPException(status_code=403, detail="This vehicle does not belong to the logged in user")

    reservation_list: list[Reservation] = reservation_model.get_reservations_by_vehicle(vehicle_id)
    return reservation_list


@router.post("/reservations/create")
async def create_reservation(reservation: ReservationCreate, current_user: User = Depends(get_current_user)):
    parking_lot = parking_lot_model.get_parking_lot_by_lid(reservation.parking_lot_id)
    if parking_lot == None:
        logger.warning("Parking lot %s does not exist", reservation.parking_lot_id)
        raise HTTPException(status_code = 404, detail = {"message": f"Parking lot does not exist"})
    
    vehicle = vehicle_model.get_one_vehicle(reservation.vehicle_id)
    if vehicle == None:
        logger.warning("Vehicle %s does not exist", reservation.vehicle_id)
        raise HTTPException(status_code = 404, detail = {"message": f"Vehicle does not exist"})

    # check if start time is later than the current time
    if reservation.start_time < datetime.now():
        raise HTTPException(status_code = 400, detail = {"message": f"invalid start time. The start time cannot be earlier than the current time. current time: {datetime.now()}, received time: {reservation.start_time}"})

    # check if the start time is later than the end time
    if reservation.start_time >= reservation.end_time:
        raise HTTPException(status_code = 400, detail = {"message": f"invalid start time. The start time cannot be later than the end time. start time: {reservation.start_time}, end time: {reservation.end_time}"})

    # Check for conflicting reservations
    conflicting_time: bool = False
    vehicle_reservations: list[Reservation] = reservation_model.get_reservations_by_vehicle(vehicle["id"])
    for existing_reservation in vehicle_reservations:
        # Check if the new reservation overlaps with an existing one
        if reservation.start_time < existing_reservation["end_time"] and reservation.end_time > existing_reservation["start_time"]:
            conflicting_time = True
            break
    if conflicting_time:
        raise HTTPException(status_code = 409, detail = {"message": f"Requested time has an overlap with another reservation for this vehicle"})

    #create a new reservation
    parking_lot = parking_lot_model.get_parking_lot_by_lid(reservation.parking_lot_id)
    #errorhandling etc.

    # Only validate discount code if one was provided
    if reservation.discount_code is not None:
        discount_code = discount_code_model.get_discount_code_by_code(reservation.discount_code)
        if discount_code is None:
            logger.error("User ID %s tried to use discount code %s, but it was not found", current_user.id, reservation.discount_code)
            raise HTTPException(status_code=404, detail={"message": "Discount code not found"})
        use_discount_code_validation(discount_code, reservation, current_user, parking_lot)
        cost = calculate_price(parking_lot, reservation, discount_code)
    else:
        cost = calculate_price(parking_lot, reservation, None)
    
    reservation_id = reservation_model.create_reservation(reservation, current_user.id, cost)
    #errorhandling etc.

    transaction = generate_payment_hash(str(reservation_id), vehicle["license_plate"])
    payment_hash = generate_transaction_validation_hash()
    payment = PaymentCreate(
        user_id=current_user.id,
        parking_lot_id=reservation.parking_lot_id,
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
    # Controleer of de reservatie bestaat
    reservation: Reservation | None = reservation_model.get_reservation_by_id(
        reservation_id
    )
    if reservation is None:
        logging.warning("User with id %s tried to delete a reservation that does not exist: %s", current_user.id, reservation_id)
        raise HTTPException(status_code=404, detail={"message": "Reservation not found"})

    # Controleer of de reservatie toebehoort aan de ingelogde gebruiker
    if reservation.user_id != current_user.id:
        logging.warning("User with id %s tried to delete a reservation that does not belong to them: %s", current_user.id, reservation_id)
        raise HTTPException(status_code=403, detail={"message": "This reservation does not belong to the logged-in user"})

    # Verwijder de reservatie
    success = reservation_model.delete_reservation(reservation_id)
    if not success:
        logging.error("Failed to delete reservation with id %s for user %s", reservation_id, current_user.id)
        raise HTTPException(status_code=500, detail={"message": "Failed to delete reservation"})

    logging.info("User with id %s successfully deleted reservation with id %s", current_user.id, reservation_id)
    raise HTTPException(detail={"message": "Reservation deleted successfully"}, status_code=200)

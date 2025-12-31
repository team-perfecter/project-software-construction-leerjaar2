import logging
from datetime import datetime
from api.auth_utils import get_current_user
from api.datatypes.user import User
from api.datatypes.payment import PaymentCreate
from fastapi import Depends, APIRouter, HTTPException, status, Body
from api.datatypes.reservation import Reservation, ReservationCreate
from api.datatypes.vehicle import Vehicle
from api.models.parking_lot_model import ParkingLotModel
from api.models.reservation_model import Reservation_model
from api.models.vehicle_model import Vehicle_model
from api.models.session_model import SessionModel
from api.models.payment_model import PaymentModel
from api.session_calculator import generate_payment_hash, generate_transaction_validation_hash, calculate_price


router = APIRouter(
    tags=["reservations"]
)

reservation_model: Reservation_model = Reservation_model()
parking_lot_model: ParkingLotModel = ParkingLotModel()
vehicle_model: Vehicle_model = Vehicle_model()
session_model: SessionModel = SessionModel()
payment_model: PaymentModel = PaymentModel()


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

@router.get("/reservations/vehicle/{vehicle_id}")
async def reservations(vehicle_id: int, current_user: User = Depends(get_current_user)):
    vehicle = vehicle_model.get_one_vehicle(vehicle_id)
    if vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    if vehicle["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="This vehicle does not belong to the logged in user")

    reservation_list: list[Reservation] = reservation_model.get_reservation_by_vehicle(vehicle_id)

    return reservation_list

@router.post("/reservations/create")
async def create_reservation(reservation: ReservationCreate, current_user: User = Depends(get_current_user)):
    parking_lot = parking_lot_model.get_parking_lot_by_lid(reservation.parking_lot_id)
    if parking_lot == None:
        raise HTTPException(status_code = 404, detail = {"message": f"Parking lot does not exist"})
    
    vehicle = vehicle_model.get_one_vehicle(reservation.vehicle_id)
    if vehicle == None:
        raise HTTPException(status_code = 404, detail = {"message": f"Vehicle does not exist"})
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
    cost = calculate_price(parking_lot, reservation)

    reservation_id = reservation_model.create_reservation(reservation, current_user.id, None, cost)

    transaction = generate_payment_hash(str(reservation_id), vehicle["license_plate"])
    payment_hash = generate_transaction_validation_hash()
    payment = PaymentCreate(
        user_id=current_user.id,
        amount=cost,
        transaction=transaction,
        hash=payment_hash
    )
    payment_id = payment_model.create_payment(payment)
    #add error handling for payment 

    reservation_model.link_payment_to_reservation(reservation_id, payment_id)
    raise HTTPException(status_code = 201, detail = {"message": f"reservation created: {reservation_id}"})

@router.delete("/reservations/delete/{reservation_id}")
async def delete_reservation(reservation_id: int, current_user: User = Depends(get_current_user)):
    # Controleer of de reservatie bestaat
    reservation: Reservation | None = reservation_model.get_reservation_by_id(reservation_id)
    if reservation is None:
        logging.warning("User with id %i tried to delete a reservation that does not exist: %i", current_user.id, reservation_id)
        raise HTTPException(status_code=404, detail={"message": "Reservation not found"})

    # Controleer of de reservatie toebehoort aan de ingelogde gebruiker
    if reservation["user_id"] != current_user.id:
        logging.warning("User with id %i tried to delete a reservation that does not belong to them: %i", current_user.id, reservation_id)
        raise HTTPException(status_code=403, detail={"message": "This reservation does not belong to the logged-in user"})

    # Verwijder de reservatie
    success = reservation_model.delete_reservation(reservation_id)
    if not success:
        logging.error("Failed to delete reservation with id %i for user %i", reservation_id, current_user.id)
        raise HTTPException(status_code=500, detail={"message": "Failed to delete reservation"})

    logging.info("User with id %i successfully deleted reservation with id %i", current_user.id, reservation_id)
    raise HTTPException(detail={"message": "Reservation deleted successfully"}, status_code=200)

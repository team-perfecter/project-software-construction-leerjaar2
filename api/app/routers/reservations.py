from datetime import datetime
from api.auth_utils import get_current_user
from api.datatypes.user import User
from fastapi import Depends, APIRouter, HTTPException
from api.datatypes.reservation import Reservation, ReservationCreate
from api.datatypes.vehicle import Vehicle
from api.models.parking_lot_model import ParkingLotModel
from api.models.reservation_model import Reservation_model
from api.models.vehicle_model import Vehicle_model

import logging
logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["reservations"]
)

reservation_model: Reservation_model = Reservation_model()
parkingLot_model: ParkingLotModel = ParkingLotModel()
vehicle_model: Vehicle_model = Vehicle_model()

@router.get("/reservations/vehicle/{vehicle_id}")
async def reservations(vehicle_id: int, user: User = Depends(get_current_user)):
    logger.info("User %i tried to retrieve reservations for vehicle %i", user.id, vehicle_id)
    vehicle = vehicle_model.get_one_vehicle(vehicle_id)
    if vehicle is None:
        logger.warning("Vehicle %i not found", vehicle_id)
        raise HTTPException(status_code=404, detail="Vehicle not found")

    if vehicle["user_id"] != user.id:
        logger.warning("Vehicle %i does not belong to user %i", vehicle_id, user.id)
        raise HTTPException(status_code=403, detail="This vehicle does not belong to the logged in user")

    reservation_list: list[Reservation] = reservation_model.get_reservation_by_vehicle(vehicle_id)
    logger.info("Found %i reservations for vehicle %i", len(reservation_list), vehicle_id)
    return reservation_list

@router.post("/reservations/create")
async def create_reservation(reservation: ReservationCreate, user: User = Depends(get_current_user)):
    logger.info("User %i tried to create a new reservation with vehicle %i on parking lot %i", user.id, reservation.vehicle_id, reservation.parking_lot_id)
    parking_lot = parkingLot_model.get_parking_lot_by_lid(reservation.parking_lot_id)
    if parking_lot == None:
        logger.warning("Parking lot %i does not exist", reservation.parking_lot_id)
        raise HTTPException(status_code = 404, detail = {"message": f"Parking lot does not exist"})
    
    
    vehicle = vehicle_model.get_one_vehicle(reservation.vehicle_id)
    if vehicle == None:
        logger.warning("Vehicle %i does not exist", reservation.vehicle_id)
        raise HTTPException(status_code = 404, detail = {"message": f"Vehicle does not exist"})
    
    conflicting_time: bool = False
    vehicle_reservations: list[Reservation] = reservation_model.get_reservation_by_vehicle(vehicle["id"])
    for reservation in vehicle_reservations:
        if reservation["start_date"] < reservation["end_date"] and reservation["end_date"] > reservation["start_date"]:
            conflicting_time = True
            break
    if conflicting_time:
        logger.warning("The reservation that user %i tried to create has an overlap with another reservation", user.id)
        raise HTTPException(status_code = 409, detail = {"message": f"Requested date has an overlap with another reservation for this vehicle"})

    # check if start date is later than the current date
    if reservation.start_date < datetime.now():
        logger.warning("Reservation not created. Start date was earlier than the current time")
        raise HTTPException(status_code = 400, detail = {"message": f"invalid start date. The start date cannot be earlier than the current date. current date: {datetime.now()}, received date: {reservation.start_date}"})

    # check if the end date is later than the start date
    if reservation.start_date >= reservation.end_date:
        logger.warning("Reservation not created. Start date was later than the end time")
        raise HTTPException(status_code = 400, detail = {"message": f"invalid start date. The start date cannot be later than the end date start date: {reservation.start_date}, end date: {reservation.end_date}"})
    
    reservation_data = {"user_id": user.id, "parking_lot_id": reservation.parking_lot_id, "vehicle_id": reservation.vehicle_id, "start_time": reservation.start_date, "end_time": reservation.end_date, "status": True}
    # create a new reservation
    reservation_create = reservation_model.create_reservation(reservation_data)
    logger.info("Reservation successfully created by user %i", user.id)
    raise HTTPException(status_code = 201, detail = {"message": f"reservation created: {reservation_create}"})

@router.delete("/reservations/delete/{reservation_id}")
async def delete_reservation(reservation_id: int, user: User = Depends(get_current_user)):
    logger.info("User %i tried to delete reservation %i", user.id, reservation_id)
    # Controleer of de reservatie bestaat
    reservation: Reservation | None = reservation_model.get_reservation_by_id(reservation_id)
    if reservation is None:
        logger.warning("Reservation not deleted. User %i tried to delete a reservation that does not exist: %i", user.id, reservation_id)
        raise HTTPException(status_code=404, detail={"message": "Reservation not found"})

    # Controleer of de reservatie toebehoort aan de ingelogde gebruiker
    if reservation["user_id"] != user.id:
        logger.warning("Reservation not deleted. User %i tried to delete a reservation that does not belong to them: %i", user.id, reservation_id)
        raise HTTPException(status_code=403, detail={"message": "This reservation does not belong to the logged-in user"})

    # Verwijder de reservatie
    success = reservation_model.delete_reservation(reservation_id)
    if not success:
        logger.error("Failed to delete reservation with id %i for user %i", reservation_id, user.id)
        raise HTTPException(status_code=500, detail={"message": "Failed to delete reservation"})

    logger.info("User with id %i successfully deleted reservation with id %i", user.id, reservation_id)
    raise HTTPException(detail={"message": "Reservation deleted successfully"}, status_code=200)

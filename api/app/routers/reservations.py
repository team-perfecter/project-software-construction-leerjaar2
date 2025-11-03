import logging

from api.auth_utils import get_current_user
from api.datatypes.user import User
from fastapi import Depends, APIRouter, HTTPException

from api.datatypes.reservation import Reservation
from api.datatypes.vehicle import Vehicle
from api.storage.reservation_storage import Reservation_storage
from api.storage.vehicle_storage import Vehicle_storage

router = APIRouter(
    tags=["reservations"]
)

reservation_storage: Reservation_storage = Reservation_storage()
parking_lot_storage: Parking_lot_storage = Parking_lot_storage()
vehicle_storage: Vehicle_modal = Vehicle_modal()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

@router.get("/reservations/{vehicle_id}")
async def reservations(vehicle_id: int, current_user: User = Depends(get_current_user)):
    vehicle: Vehicle | None = vehicle_storage.get_vehicle_by_id(vehicle_id)
    user_id: int = current_user.id
    if vehicle is None:
        logging.warning("A user with the ID %i tried to retrieve a vehicle that doesnt exist: %i", user_id, vehicle_id)
        raise HTTPException(status_code=404, detail="Vehicle not found")

    if vehicle.user_id != user_id:
        logging.warning("A user with the ID %i tried to retrieve a vehicle that doesnt belong to the user: %i", user_id, vehicle.user_id)
        raise HTTPException(status_code=403, detail="This vehicle does not belong to the logged in user")

    reservation_list: list[Reservation] = reservation_storage.get_reservations_by_vehicle_id(vehicle_id)

    return reservation_list


@router.post("/create_reservation")
async def create_reservation(vehicle_id: int, parking_lot_id: int, start_date: datetime, end_date: datetime, current_user: User = Depends(get_current_user)):

    # check for missing fields
    missing_fields: list[str] = []
    if not vehicle_id:
        missing_fields.append("vehicle")
    if not parking_lot_id:
        missing_fields.append("parking lot")
    if not start_date:
        missing_fields.append("start date")
    if not end_date:
        missing_fields.append("end date")
    if len(missing_fields) > 0:
        logging.warning("A user tried to create a new reservation, but did not fill in the following fields: %s", missing_fields)
        raise HTTPException(status_code = 400, detail = {"missing_fields": missing_fields})
    
    # check if the vehicle and parking lot exist

    parking_lot = parking_lot_storage.get_parking_lot_by_id(parking_lot_id)
    if parking_lot == None:
        logging.warning("A user with the id of %i tried to create a new reservation, but the requested parking lot does not exist: %i", current_user.id, parking_lot_id)
        raise HTTPException(status_code = 404, detail = {"message": f"Parking lot does not exist"})
    
    vehicle: Vehicle = vehicle_storage.get_one_vehicle(vehicle_id)
    if vehicle == None:
        logging.warning("A user with the id of %i tried to create a new reservation, but the requested vehicle does not exist: %i", current_user.id, vehicle_id)
        raise HTTPException(status_code = 404, detail = {"message": f"Vehicle does not exist"})


    # check if the vehicle belongs to the user
    if vehicle.user_id != current_user.id:
        logging.warning("A user with the id of %i tried to create a new reservation, but the requested vehicle with the id %i does not belong to this user", current_user.id, vehicle_id)
        raise HTTPException(status_code = 401, detail = {"message": f"Vehicle does not belong to this user"})

    # check if the parking lot has space left
    if parking_lot.reserved <= 0:
        logging.warning("A user with the id of %i tried to create a new reservation, but the requested parking lot with the id %i is full", current_user.id, parking_lot_id)
        raise HTTPException(status_code = 401, detail = {"message": f"No more space in this parking lot"})

    # check if the vehicle already has a reservation around that time
    conflicting_time: bool = False
    vehicle_reservations: list[Reservation] = Reservation_storage.get_reservation_by_vehicle(vehicle.id)
    for reservation in vehicle_reservations:
        if start_date < reservation.end_time and end_date > reservation.start_time:
            conflicting_time = True
            break
    if conflicting_time:
        logging.warning("A user with the id of %i and with a vehicle with the id %i tried to create a reservation, but there was a time overlap with another reservation", current_user.id, vehicle_id)
        raise HTTPException(status_code = 401, detail = {"message": f"Requested date has an overlap with another reservation for this vehicle"})

    # check if start date is later than the current date
    if start_date <= datetime.now:
        logging.warning("A user with the id of %i tried to create a new reservation, but the current date was later than the start date. current date: %s start date %s", current_user.id, datetime.now, start_date)
        raise HTTPException(status_code = 403, detail = {"message": f"invalid start date. The start date cannot be earlier than the current date. current date: {datetime.now}, received date: {start_date}"})

    # check if the end date is later than the start date
    if start_date >= end_date:
        logging.warning("A user with the id of %i tried to create a new reservation, but the start date was later than the end date. start date: %s end date %s", current_user.id, start_date, end_date)
        raise HTTPException(status_code = 403, detail = {"message": f"invalid start date. The start date cannot be later than the end date start date: {start_date}, end date: {end_date}"})

    # create a new reservation
    storage.post_reservation(Reservation(None, vehicle_id, current_user.id, parking_lot_id, start_date, end_date, "status", datetime.now, parking_lot.tariff))
    logging.info("A user with the id of %i has successfully created a new reservation with the vehicle id %i at parking lot %i", current_user.id, vehicle_id, parking_lot_id)
    return JSONResponse(content={"message": "Reservation created successfully"}, status_code=201)

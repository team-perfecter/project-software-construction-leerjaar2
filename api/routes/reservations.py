from datatypes.reservation import Reservation
from storage.reservation_storage import Reservation_storage
from storage.parking_lot_storage import Parking_lot_storage
from datetime import datetime
from fastapi import FastAPI, HTTPException
import logging

app = FastAPI()

storage: Reservation_storage = Reservation_storage()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

app.post("/create_reservation")
async def create_reservation(vehicle_id: int, parking_lot_id: int, start_date: datetime, end_date: datetime):
    # check if the user is logged in

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

    parking_lot_storage: Parking_lot_storage = Parking_lot_storage()
    parking_lot = parking_lot_storage.get_parking_lot_by_id(parking_lot_id)
    if parking_lot == None:
        logging.warning("A user with the id of %i tried to create a new reservation, but the requested parking lot does not exist: %i", user.id, parking_lot_id)
        raise HTTPException(status_code = 404, detail = {"message": f"Parking lot does not exist"})


    # check if the vehicle belongs to the user

    # check if parking lot exists

    # check if the parking lot has space left

    # check if the vehicle already has a reservation around that time

    # check if start date is later than the current date
    if start_date <= datetime.now:
        logging.warning("A user with the id of %i tried to create a new reservation, but the current date was later than the start date. current date: %s start date %s", user.id, datetime.now, start_date)
        raise HTTPException(status_code = 403, detail = {"message": f"invalid start date. The start date cannot be earlier than the current date. current date: {datetime.now}, received date: {start_date}"})

    # check if the end date is later than the start date
    if start_date >= end_date:
        logging.warning("A user with the id of %i tried to create a new reservation, but the start date was later than the end date. start date: %s end date %s", user.id, start_date, end_date)
        raise HTTPException(status_code = 403, detail = {"message": f"invalid start date. The start date cannot be later than the end date start date: {start_date}, end date: {end_date}"})

    # create a new reservation
    storage.post_reservation(Reservation(None, vehicle_id, user.id, parking_lot_id, start_date, end_date, "status", datetime.now, parking_lot.tariff))
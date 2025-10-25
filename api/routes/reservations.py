from datatypes.reservation import Reservation
from storage.reservation_storage import Reservation_storage
from datetime import date
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
async def create_reservation(vehicle_id: int, parking_lot_id: int, start_date: date, end_date: date):
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

    # check if the vehicle belongs to the user

    # check if parking lot exists

    # check if the parking lot has space left

    # check if the vehicle already has a reservation around that time

    # check if start date is later than the current date

    # check if the end date is later than the start date

    # create a new session
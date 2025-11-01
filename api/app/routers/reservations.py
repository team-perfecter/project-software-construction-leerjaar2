import logging

from api.auth_utils import get_current_user
from api.datatypes.user import User
from fastapi import APIRouter, HTTPException

from api.datatypes.reservation import Reservation
from api.datatypes.vehicle import Vehicle
from api.storage.reservation_storage import Reservation_storage
from api.storage.vehicle_storage import Vehicle_storage

router = APIRouter(
    tags=["reservations"]
)

vehicle_storage: Vehicle_storage = Vehicle_storage()
reservation_storage: Reservation_storage = Reservation_storage()

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

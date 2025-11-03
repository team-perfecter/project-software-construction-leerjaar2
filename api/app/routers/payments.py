import logging

from api.auth_utils import get_current_user
from api.datatypes.user import User
from fastapi import Depends, APIRouter, HTTPException

from api.storage.payment_storage import Payment_storage
from api.storage.profile_storage import Profile_storage

router = APIRouter(
    tags=["reservations"]
)

payment_storage: Payment_storage = Payment_storage()
profile_storage: Profile_storage = Profile_storage()

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

@router.get("/payments")
async def get_payments(current_user: User = Depends(get_current_user)):
    user_id: int = current_user.id
    payments_list = payment_storage.get_payments_by_user(user_id)

    logging.info("Retrieved %i payments for user ID %i", len(payments_list), user_id)
    return payments_list

@router.get("/payments/{user_id}")
async def get_payments(user_id: int):
    payments_list = payment_storage.get_payments_by_user(user_id)

    logging.info("Retrieved %i payments for user ID %i", len(payments_list), user_id)
    return payments_list
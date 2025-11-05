import logging

from api.auth_utils import get_current_user
from api.datatypes.user import User
from fastapi import Depends, APIRouter, HTTPException

from api.storage.payment_storage import Payment_storage
from api.storage.profile_storage import Profile_storage

from datetime import datetime

router = APIRouter(
    tags=["payments"]
)

payment_storage: Payment_storage = Payment_storage()
profile_storage: Profile_storage = Profile_storage()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

@router.get("/me")
async def get_payments(current_user: User = Depends(get_current_user)):
    user_id: int = current_user.id
    payments_list = payment_storage.get_payments_by_user(user_id)

    logging.info("Retrieved %i payments for user ID %i", len(payments_list), user_id)
    return payments_list

@router.get("/open/me")
async def get_open_payments(current_user: User = Depends(get_current_user)):
    user_id: int = current_user.id
    payments_list = payment_storage.get_open_payments_by_user(user_id)

    logging.info("Retrieved %i payments for user ID %i", len(payments_list), user_id)
    return payments_list

@router.get("/{user_id}")
async def get_payments_by_user(user_id: int):
    user = profile_storage.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    payments_list = payment_storage.get_payments_by_user(user_id)

    logging.info("Retrieved %i payments for user ID %i", len(payments_list), user_id)
    return payments_list

@router.get("/{user_id}/open")
async def get_open_payments_by_user(user_id: int):
    user = profile_storage.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    payments_list = payment_storage.get_open_payments_by_user(user_id)

    logging.info("Retrieved %i payments for user ID %i", len(payments_list), user_id)
    return payments_list

@router.post("/{payment_id}/pay")
async def make_payment(payment_id: int, current_user: User = Depends(get_current_user)):
    payment = payment_storage.get_payment_by_id(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    if payment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No permission to pay this bill")
    
    if payment.completed_at is not None:
        raise HTTPException(status_code =400, detail="Payment has already been paid")
    
    payment.completed_at = datetime.now()
    update = payment_storage.update_payment(payment)
    if not update:
        raise HTTPException(status_code=500, detail="Payment has failed")
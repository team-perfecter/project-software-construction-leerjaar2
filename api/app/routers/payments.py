import logging

from api.auth_utils import get_current_user
from api.datatypes.user import User
from fastapi import Depends, APIRouter, HTTPException
from api.models.payment_model import PaymentModel
from api.models.user_model import UserModel

from datetime import datetime

router = APIRouter(
    tags=["payments"]
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

@router.get("/me")
async def get_payments(current_user: User = Depends(get_current_user)):
    user_id: int = current_user.id
    payments_list = UserModel.get_payments_by_user(user_id)

    logging.info("Retrieved %i payments for user ID %i", len(payments_list), user_id)
    return payments_list

@router.get("/open/me")
async def get_open_payments(current_user: User = Depends(get_current_user)):
    user_id: int = current_user.id
    payments_list = PaymentModel.get_open_payments_by_user(user_id)

    logging.info("Retrieved %i payments for user ID %i", len(payments_list), user_id)
    return payments_list

@router.get("/{user_id}")
async def get_payments_by_user(user_id: int, current_user: User = Depends(get_current_user)):
    user = UserModel.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    payments_list = PaymentModel.get_payments_by_user(user_id)

    logging.info("Retrieved %i payments for user ID %i", len(payments_list), user_id)
    return payments_list

@router.get("/{user_id}/open")
async def get_open_payments_by_user(user_id: int, current_user: User = Depends(get_current_user)):
    user = UserModel.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    payments_list = PaymentModel.get_open_payments_by_user(user_id)

    logging.info("Retrieved %i payments for user ID %i", len(payments_list), user_id)
    return payments_list

@router.post("/{payment_id}/pay")
async def make_payment(payment_id: int, current_user: User = Depends(get_current_user)):
    payment = PaymentModel.get_payment_by_payment_id(payment_id)
    if not payment:
        logging.warning("A user with the id of %i tried to make a payment, but the requested payment does not exist: %i", current_user.id, payment_id)
        raise HTTPException(status_code=404, detail="Payment not found")
    
    
    if payment.user_id != current_user.id:
        logging.warning("A user with the id of %i tried to make a payment, but the requested payment %i does not belong to the user", current_user.id, payment_id)
        raise HTTPException(status_code=403, detail="No permission to pay this bill")
    
    if payment.completed is not False:
        logging.warning("A user with the id of %i tried to make a payment, but the requested payment %i has already been paid", current_user.id, payment_id)
        raise HTTPException(status_code =400, detail="Payment has already been paid")
    
    payment.completed = True
    update = PaymentModel.update_payment(payment)
    if not update:
        logging.warning("A user with the id of %i tried to make a payment, but the requested payment %i has failed", current_user.id, payment_id)
        raise HTTPException(status_code=500, detail="Payment has failed")
    logging.info("A user with the id of %i tried to made a payment: %i", current_user.id, payment_id)
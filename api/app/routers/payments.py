import logging
from fastapi import APIRouter, HTTPException, Depends
from api.datatypes.user import User
from api.datatypes.payment import PaymentCreate
from api.models.payment_model import PaymentModel
from api.models.user_model import UserModel
from api.auth_utils import get_current_user

router = APIRouter(
    tags=["payments"]
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

@router.post("/payments", status_code=201) #readd currentuser
async def create_payment(p: PaymentCreate):
    created = PaymentModel.create_payment(p)
    if not created:
        raise HTTPException(status_code=500, detail="Failed to create payment")
    logging.info("Created new payment for user_id %i", p.user_id)
    return {"message": "Payment created successfully"}

@router.get("/me") # only check if it works 
async def get_my_payments(current_user: User = Depends(get_current_user)):
    payments_list = UserModel.get_payments_by_user(current_user.id)
    logging.info("Retrieved %i payments for user ID %i", len(payments_list), current_user.id)
    return payments_list

@router.get("/payments/user/{user_id}") #readd current user check
async def get_payments_by_user(user_id: int):
    payments_list = PaymentModel.get_payments_by_user(user_id)
    logging.info("Retrieved %i payments for user ID %i", len(payments_list), user_id)
    return payments_list

@router.get("/payments/user/{user_id}/open") #readd currentuser check
async def get_open_payments_by_user(user_id: int):
    payments_list = PaymentModel.get_open_payments_by_user(user_id)
    logging.info("Retrieved %i payments for user ID %i", len(payments_list), user_id)
    return payments_list

@router.post("/payments/{payment_id}/pay") #readd current user check
async def pay_payment(payment_id: int):
    payment = PaymentModel.get_payment_by_payment_id(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    if payment["completed"]:
        raise HTTPException(status_code=400, detail="Payment has already been paid")
    update = PaymentModel.mark_payment_completed(payment_id)
    if not update:
        raise HTTPException(status_code=500, detail="Payment has failed")
    return {"message": "Payment completed successfully"}

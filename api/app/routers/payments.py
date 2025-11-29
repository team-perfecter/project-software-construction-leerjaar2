import logging
from fastapi import APIRouter, HTTPException, Depends
from api.datatypes.user import User, UserRole
from api.datatypes.payment import PaymentCreate, PaymentUpdate, Payment
from api.models.payment_model import PaymentModel
from api.models.user_model import UserModel
from api.auth_utils import get_current_user, require_role

router = APIRouter(
    tags=["payments"]
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

@router.post("/payments", status_code=201) #readd currentuser
async def create_payment(p: PaymentCreate, current_user: User = Depends(require_role(UserRole.PAYMENTADMIN, UserRole.SUPERADMIN))):
    print("CREATED CHECK CHECK CHECK")
    created = PaymentModel.create_payment(p)
    if not created:
        raise HTTPException(status_code=500, detail="Failed to create payment")
    logging.info("Created new payment for user_id %i", p.user_id)
    return {"message": "Payment created successfully"}

@router.get("/payments/me") # only check if it works 
async def get_my_payments(current_user: User = Depends(require_role(UserRole.PAYMENTADMIN, UserRole.SUPERADMIN))):
    payments_list = PaymentModel.get_payments_by_user(current_user.id)
    logging.info("Retrieved %i payments for user ID %i", len(payments_list), current_user.id)
    return payments_list

@router.get("/payments/me/open") #readd currentuser check
async def get_open_payments_by_user(current_user: User = Depends(require_role(UserRole.PAYMENTADMIN, UserRole.SUPERADMIN))):
    payments_list = PaymentModel.get_open_payments_by_user(current_user.id)
    logging.info("Retrieved %i payments for user ID %i", len(payments_list), current_user.id)
    return payments_list

@router.get("/payments/user/{user_id}") #readd current user check
async def get_payments_by_user(user_id: int):
    payments_list = PaymentModel.get_payments_by_user(user_id)
    logging.info("Retrieved %i payments for user ID %i", len(payments_list), user_id)
    return payments_list

@router.get("/payments/user/{user_id}/open") #readd currentuser check
async def get_open_payments_by_user(user_id: int, current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.SUPERADMIN))):
    payments_list = PaymentModel.get_open_payments_by_user(user_id)
    logging.info("Retrieved %i payments for user ID %i", len(payments_list), user_id)
    return payments_list

@router.post("/payments/{payment_id}/pay") #readd current user check
async def pay_payment(payment_id: int, current_user: User = Depends(get_current_user)):
    payment = PaymentModel.get_payment_by_payment_id(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    if payment["completed"]:
        raise HTTPException(status_code=400, detail="Payment has already been paid")
    update = PaymentModel.mark_payment_completed(payment_id)
    if not update:
        raise HTTPException(status_code=500, detail="Payment has failed")
    return {"message": "Payment completed successfully"}

@router.put("/payments/{payment_id}")
async def update_payment(payment_id: int, p: PaymentUpdate, current_user: User = Depends(require_role(UserRole.PAYMENTADMIN, UserRole.SUPERADMIN))):
    user_model: UserModel = UserModel()
    user = user_model.get_user_by_id(p.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    payment = PaymentModel.get_payment_by_payment_id(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    update = PaymentModel.update_payment(payment_id, p)
    if not update:
        raise HTTPException(status_code=500, detail="Payment has failed")
    return {"message": "Payment updated successfully"}

@router.delete("/payments/{payment_id}")
async def delete_payment(payment_id: int, current_user: User = Depends(require_role(UserRole.PAYMENTADMIN, UserRole.SUPERADMIN))):
    payment = PaymentModel.get_payment_by_payment_id(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    delete = PaymentModel.delete_payment(payment_id)
    if not delete:
        raise HTTPException(status_code=500, detail="Payment has failed")
    return {"message": "Payment deleted successfully"}

@router.post("/payments/{payment_id}/request_refund")
async def request_refund(payment_id: int, current_user: User = Depends(get_current_user)):
    payment = PaymentModel.get_payment_by_payment_id(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    if not payment["completed"]:
        raise HTTPException(status_code=400, detail="Payment has not yet been paid")
    if payment["refund_requested"]:
        raise HTTPException(status_code=400, detail="Refund has already been requested")
    update = PaymentModel.mark_refund_request(payment_id)
    if not update:
        raise HTTPException(status_code=500, detail="Request has failed")
    return {"message": "Refund reuested successfully"}

@router.get("/payments/refunds")
async def get_refund_requests(user_id: int | None = None, current_user: User = Depends(require_role(UserRole.PAYMENTADMIN, UserRole.SUPERADMIN))):
    if user_id:    
        user_model: UserModel = UserModel()
        user = user_model.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
    refunds = PaymentModel.get_refund_requests(user_id)
    return refunds

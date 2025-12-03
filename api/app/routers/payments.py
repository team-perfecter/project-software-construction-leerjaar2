import logging
from fastapi import APIRouter, HTTPException, Depends
from api.datatypes.user import User, UserRole
from api.datatypes.payment import PaymentCreate, PaymentUpdate
from api.models.payment_model import PaymentModel
from api.models.user_model import UserModel
from api.auth_utils import get_current_user, require_role

router = APIRouter(
    tags=["payments"]
)

user_model: UserModel = UserModel()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


@router.post("/payments", status_code=201)
async def create_payment(p: PaymentCreate,
                         current_user: User = Depends(require_role(
                          UserRole.PAYMENTADMIN, UserRole.SUPERADMIN))):
    created = PaymentModel.create_payment(p)
    if not created:
        logging.info("Admin ID %i tried to create a payment, but failed",
                     current_user.id)
        raise HTTPException(status_code=500,
                            detail="Failed to create payment")
    logging.info("Admin ID %i created new payment for user_id %i",
                 current_user.id, p.user_id)
    return {"message": "Payment created successfully"}


@router.get("/payments/me")
async def get_my_payments(current_user: User = Depends(get_current_user)):
    payments_list = PaymentModel.get_payments_by_user(current_user.id)
    if not payments_list:
        logging.info("User ID %i tried retrieving their own payments, "
                     "but none were found",
                     current_user.id)
        raise HTTPException(status_code=404,
                            detail="No payments not found")
    logging.info("User ID %i retrieved their own payments",
                 current_user.id)
    return payments_list


@router.get("/payments/me/open")
async def get_my_open_payments(current_user: User = Depends(get_current_user)):
    payments_list = PaymentModel.get_open_payments_by_user(current_user.id)
    if not payments_list:
        logging.info("User ID %i tried retrieving their own payments"
                     ", but none were found", current_user.id)
        raise HTTPException(status_code=404, detail="No payments not found")
    logging.info("User ID %i retrieved their own payments",
                 current_user.id)
    return payments_list


@router.get("/payments/user/{user_id}")
async def get_payments_by_user(user_id: int,
                               current_user: User = Depends(require_role(
                                UserRole.PAYMENTADMIN, UserRole.SUPERADMIN))):
    user = user_model.get_user_by_id(user_id)
    if not user:
        logging.info("Admin ID %i tried searching for nonexistent User ID %i",
                     current_user.id, user_id)
        raise HTTPException(status_code=404, detail="No user not found")
    payments_list = PaymentModel.get_payments_by_user(user_id)
    if not payments_list:
        logging.info("Admin ID %i tried retrieving payments from User ID %i, "
                     "but none were found",
                     current_user.id, user_id)
        raise HTTPException(status_code=404, detail="No payments not found")
    logging.info("Admin ID %i retrieved payments of User ID %i",
                 current_user.id, user_id)
    return payments_list


@router.get("/payments/user/{user_id}/open")
async def get_open_payments_by_user(user_id: int,
                                    current_user: User = Depends(require_role(
                                     UserRole.ADMIN, UserRole.SUPERADMIN))):
    user = user_model.get_user_by_id(user_id)
    if not user:
        logging.info("Admin ID %i tried searching for nonexistent User ID %i",
                     current_user.id, user_id)
        raise HTTPException(status_code=404, detail="No user not found")
    payments_list = PaymentModel.get_open_payments_by_user(user_id)
    if not payments_list:
        logging.info("Admin ID %i tried retrieving payments from User ID %i, "
                     "but none were found", current_user.id, user_id)
        raise HTTPException(status_code=404,
                            detail="No payments not found")
    logging.info("Admin ID %i retrieved payments of User ID %i",
                 current_user.id, user_id)
    return payments_list


@router.post("/payments/{payment_id}/pay")
async def pay_payment(payment_id: int,
                      current_user: User = Depends(get_current_user)):
    payment = PaymentModel.get_payment_by_payment_id(payment_id)
    if not payment:
        logging.info("User ID %i searched for Payment ID %i, "
                     "but nothing was found",
                     current_user.id, payment_id)
        raise HTTPException(status_code=404,
                            detail="Payment not found")
    if payment["user_id"] != current_user.id:
        logging.info("User ID %i tried paying Payment ID %i, "
                     "but it does not belong to user",
                     current_user.id, payment_id)
        raise HTTPException(status_code=403,
                            detail="This payment does not belong to this user")
    if payment["completed"]:
        logging.info("User ID %i tried paying for Payment ID %i, "
                     "but payment was already completed",
                     current_user.id, payment_id)
        raise HTTPException(status_code=400,
                            detail="Payment has already been paid")
    update = PaymentModel.mark_payment_completed(payment_id)
    if not update:
        logging.info("Payment ID %i payment failed by User ID %i",
                     payment_id, current_user.id)
        raise HTTPException(status_code=500,
                            detail="Payment has failed")
    logging.info("Payment ID %i has succesfully been paid by User ID %i",
                 payment_id, current_user.id)
    return {"message": "Payment completed successfully"}


@router.put("/payments/{payment_id}")
async def update_payment(payment_id: int,
                         p: PaymentUpdate,
                         current_user: User = Depends(require_role(
                          UserRole.PAYMENTADMIN, UserRole.SUPERADMIN))):
    payment = PaymentModel.get_payment_by_payment_id(payment_id)
    if not payment:
        logging.info("Admin ID %i tried updating Payment ID %i, "
                     "but payment does not exist", current_user.id, payment_id)
        raise HTTPException(status_code=404,
                            detail="Payment not found")
    user = user_model.get_user_by_id(p.user_id)
    if not user:
        logging.info("Admin ID %i tried changing Payment ID %i to User ID %i, "
                     "but user does not exist.",
                     current_user.id, payment_id, p["user_id"])
        raise HTTPException(status_code=404,
                            detail="User not found")
    update = PaymentModel.update_payment(payment_id, p)
    if not update:
        logging.info("Admin ID %i failed updating Payment ID %i",
                     current_user.id, payment_id)
        raise HTTPException(status_code=500,
                            detail="Payment has failed")
    return {"message": "Payment updated successfully"}


@router.get("/payments/refunds")
async def get_refund_requests(user_id: int | None = None,
                              current_user: User = Depends(require_role(
                               UserRole.PAYMENTADMIN, UserRole.SUPERADMIN))):
    if user_id:
        user = user_model.get_user_by_id(user_id)
        if not user:
            logging.info("Admin ID %i tried getting refunds from"
                         "nonexistent User ID %i",
                         current_user.id, user_id)
            raise HTTPException(status_code=404,
                                detail="User not found")
    refunds = PaymentModel.get_refund_requests(user_id)
    if not refunds:
        logging.info("Admin ID %i tried getting refunds, "
                     "but none were found", current_user.id)
        raise HTTPException(status_code=404,
                            detail="No refunds found")
    logging.info("Admin ID %i retrieved refunds",
                 current_user.id)
    return refunds


@router.post("/payments/{payment_id}/request_refund")
async def request_refund(payment_id: int,
                         current_user: User = Depends(get_current_user)):
    payment = PaymentModel.get_payment_by_payment_id(payment_id)
    if not payment:
        raise HTTPException(status_code=404,
                            detail="Payment not found")
    if payment["user_id"] != current_user.id:
        logging.info("User ID %i tried request refund for Payment ID %i, "
                     "but it does not belong to user",
                     current_user.id, payment_id)
        raise HTTPException(status_code=403,
                            detail="This payment does not belong to this user")
    if not payment["completed"]:
        raise HTTPException(status_code=400,
                            detail="Payment has not yet been paid")
    if payment["refund_requested"]:
        raise HTTPException(status_code=400,
                            detail="Refund has already been requested")
    update = PaymentModel.mark_refund_request(payment_id)
    if not update:
        raise HTTPException(status_code=500,
                            detail="Request has failed")
    return {"message": "Refund reuested successfully"}


@router.get("/payments/{payment_id}")
async def get_payment_by_id(payment_id: int,
                            current_user: User = Depends(require_role(
                             UserRole.PAYMENTADMIN, UserRole.SUPERADMIN))):
    payment = PaymentModel.get_payment_by_payment_id(payment_id)
    if not payment:
        logging.info("Admin ID %i tried to delete nonexistent Payment ID %i",
                     current_user.id, payment_id)
        raise HTTPException(status_code=404,
                            detail="Payment not found")
    logging.info("Admin ID %i retrieved Payment ID %i",
                 current_user.id, payment_id)
    return payment


@router.delete("/payments/{payment_id}")
async def delete_payment(payment_id: int,
                         current_user: User = Depends(require_role(
                          UserRole.PAYMENTADMIN, UserRole.SUPERADMIN))):
    payment = PaymentModel.get_payment_by_payment_id(payment_id)
    if not payment:
        logging.info("Admin ID %i tried to delete nonexistent Payment ID %i",
                     current_user.id, payment_id)
        raise HTTPException(status_code=404, detail="Payment not found")
    delete = PaymentModel.delete_payment(payment_id)
    if not delete:
        logging.info("Admin ID %i tried to delete Payment ID %i, but failed",
                     current_user.id, payment_id)
        raise HTTPException(status_code=500, detail="Deletion has failed")
    logging.info("Admin ID %i deleted Payment ID %i",
                 current_user.id, payment_id)
    return {"message": "Payment deleted successfully"}


# grand refund method

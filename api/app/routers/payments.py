"""
This file contains all endpoints related to payments.
"""

import logging

from fastapi import APIRouter, HTTPException, Depends
from api.datatypes.user import User, UserRole
from api.datatypes.payment import PaymentCreate, PaymentUpdate
from api.models.payment_model import PaymentModel
from api.models.user_model import UserModel
from api.models.parking_lot_model import ParkingLotModel
from api.auth_utils import get_current_user, require_role
from api.auth_utils import user_can_manage_lot, get_current_user_optional

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["payments"]
)

user_model: UserModel = UserModel()
parking_lot_model: ParkingLotModel = ParkingLotModel()


@router.post("/payments", status_code=201)
async def create_payment(
    p: PaymentCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new payment for a user.

    Args:
        p (PaymentCreate): The payment data to create.
        current_user (User): The currently authenticated admin user.

    Raises:
        HTTPException: If payment creation fails (500).

    Returns:
        dict: Success message if payment is created.
    """
    logger.info(f"payment trying to be created:{p}")
    user = user_model.get_user_by_id(p.user_id)
    if not user:
        logger.warning("Admin ID %s tried creating a payment for "
                       "nonexistent User %s",
                       current_user.id, p.user_id)
        raise HTTPException(status_code=404, detail="No user not found")
    lot = parking_lot_model.get_parking_lot_by_lid(p.parking_lot_id)
    if not lot:
        logger.warning("Admin ID %s tried creating a payment "
                       "for nonexistent Lot %s",
                       current_user.id, p.parking_lot_id)
        raise HTTPException(status_code=404, detail="No parking lot not found")
    if not user_can_manage_lot(current_user, p.parking_lot_id,
                               for_payments=True):
        raise HTTPException(status_code=403,
                            detail="Not enough permissions for this lot")

    created = PaymentModel.create_payment(p)
    if not created:
        logger.error("Admin ID %s tried to create a payment, but failed",
                     current_user.id)
        raise HTTPException(status_code=500, detail="Failed to create payment")
    logger.info("Admin ID %s created new payment for user_id %s",
                current_user.id, p.user_id)
    return {"message": "Payment created successfully"}


@router.get("/payments/me")
async def get_my_payments(current_user: User = Depends(get_current_user)):
    """
    Retrieve all payments belonging to the current authenticated user.

    Args:
        current_user (User): The currently authenticated user.

    Raises:
        HTTPException: If no payments are found (404).

    Returns:
        list[dict]: List of payments for the current user.
    """
    payments_list = PaymentModel.get_payments_by_user(current_user.id)
    if not payments_list:
        logger.warning("User ID %s tried retrieving their own payments, "
                       "but none were found",
                       current_user.id)
        raise HTTPException(status_code=404,
                            detail="No payments not found")
    logger.info("User ID %s retrieved their own payments",
                current_user.id)
    return payments_list


@router.get("/payments/me/open")
async def get_my_open_payments(current_user: User = Depends(get_current_user)):
    """
    Retrieve all open (unpaid) payments for the current authenticated user.

    Args:
        current_user (User): The currently authenticated user.

    Raises:
        HTTPException: If no open payments are found (404).

    Returns:
        list[dict]: List of open payments for the current user.
    """
    payments_list = PaymentModel.get_open_payments_by_user(current_user.id)
    if not payments_list:
        logger.warning("User ID %s tried retrieving their own payments"
                       ", but none were found", current_user.id)
        raise HTTPException(status_code=404, detail="No payments not found")
    logger.info("User ID %s retrieved their own payments",
                current_user.id)
    return payments_list


@router.get("/payments/user/{user_id}")
async def get_payments_by_user(user_id: int,
                               current_user: User = Depends(require_role(
                                UserRole.PAYMENTADMIN, UserRole.SUPERADMIN))):
    """
    Retrieve all payments for a specific user.

    Args:
        user_id (int): The ID of the user whose payments are requested.
        current_user (User): The currently authenticated admin user.

    Raises:
        HTTPException: If user does not exist (404) or if no payments exist (404).

    Returns:
        list[dict]: List of payments for the specified user.
    """
    user = user_model.get_user_by_id(user_id)
    if not user:
        logger.warning("Admin ID %s tried searching for nonexistent User %s",
                       current_user.id, user_id)
        raise HTTPException(status_code=404, detail="No user not found")
    payments_list = PaymentModel.get_payments_by_user(user_id)
    if not payments_list:
        logger.warning("Admin ID %s tried retrieving payments from User %s, "
                       "but none were found",
                       current_user.id, user_id)
        raise HTTPException(status_code=404, detail="No payments not found")
    logger.info("Admin ID %s retrieved payments of User ID %s",
                current_user.id, user_id)
    return payments_list


@router.get("/payments/user/{user_id}/open")
async def get_open_payments_by_user(
    user_id: int,
    current_user: User = Depends(require_role(
        UserRole.SUPERADMIN, UserRole.PAYMENTADMIN))
):
    """
    Retrieve all open (unpaid) payments for a specific user.

    Args:
        user_id (int): The ID of the user whose open payments are requested.
        current_user (User): The currently authenticated admin user.

    Raises:
        HTTPException: If user does not exist (404) or no open payments found (404).

    Returns:
        list[dict]: List of open payments for the specified user.
    """
    user = user_model.get_user_by_id(user_id)
    if not user:
        logger.warning("Admin ID %s tried searching for nonexistent User %s",
                       current_user.id, user_id)
        raise HTTPException(status_code=404, detail="No user not found")
    payments_list = PaymentModel.get_open_payments_by_user(user_id)
    if not payments_list:
        logger.warning("Admin ID %s tried retrieving payments from User %s, "
                       "but none were found", current_user.id, user_id)
        raise HTTPException(status_code=404,
                            detail="No payments not found")
    logger.info("Admin ID %s retrieved payments of User ID %s",
                current_user.id, user_id)
    return payments_list


@router.post("/payments/{payment_id}/pay")
async def pay_payment(payment_id: int,
                      current_user: User | None = Depends(get_current_user_optional)):
    """
    Mark a payment as completed (paid) by the current user.

    Args:
        payment_id (int): The ID of the payment to mark as completed.
        current_user (User): The currently authenticated user.

    Raises:
        HTTPException: 
            404 if payment does not exist.
            403 if payment does not belong to user.
            400 if payment is already completed.
            500 if marking payment as completed fails.

    Returns:
        dict: Success message if payment was completed.
    """
    payment = PaymentModel.get_payment_by_payment_id(payment_id)
    if current_user is None:
        user_id = "Guest"
    else:
        user_id = current_user.id
    if not payment:
        logger.warning("User ID %s searched for Payment ID %s, "
                       "but nothing was found",
                       user_id, payment_id)
        raise HTTPException(status_code=404,
                            detail="Payment not found")
    if current_user is not None and payment["user_id"] != current_user.id:
        logger.warning("User ID %s tried paying Payment ID %s, "
                       "but it does not belong to user",
                       user_id, payment_id)
        raise HTTPException(status_code=403,
                            detail="This payment does not belong to this user")
    if current_user is None and payment["user_id"] is not None:
        logger.warning("Guest tried paying Payment ID %s, "
                       "but it does not belong to guest",
                       payment_id)
        raise HTTPException(status_code=403,
                            detail="This payment does not belong to this user")
    if payment["completed"]:
        logger.warning("User ID %s tried paying for Payment ID %s, "
                       "but payment was already completed",
                       user_id, payment_id)
        raise HTTPException(status_code=400,
                            detail="Payment has already been paid")
    update = PaymentModel.mark_payment_completed(payment_id)
    if not update:
        logging.info("Payment ID %s payment failed by User ID %s",
                     payment_id, user_id)
        raise HTTPException(status_code=500,
                            detail="Payment has failed")
    logger.info("Payment ID %s has succesfully been paid by User ID %s",
                payment_id, user_id)
    return {"message": "Payment completed successfully"}


@router.put("/payments/{payment_id}")
async def update_payment(payment_id: int,
                         p: PaymentCreate,
                         current_user: User = Depends(require_role(
                          UserRole.PAYMENTADMIN, UserRole.SUPERADMIN))):
    """
    Update an existing payment with new data.

    Args:
        payment_id (int): The ID of the payment to update.
        p (PaymentUpdate): The updated payment data.
        current_user (User): The currently authenticated admin user.

    Raises:
        HTTPException:
            404 if payment or user does not exist.
            500 if updating payment fails.

    Returns:
        dict: Success message if payment was updated.
    """
    payment = PaymentModel.get_payment_by_payment_id(payment_id)
    if not payment:
        logger.warning("Admin ID %s tried updating Payment ID %s, "
                       "but payment does not exist", current_user.id,
                       payment_id)
        raise HTTPException(status_code=404,
                            detail="Payment not found")
    if not user_can_manage_lot(current_user, payment["parking_lot_id"],
                               for_payments=True):
        raise HTTPException(status_code=403,
                            detail="Not enough permissions for this lot")
    update_fields = p.dict(exclude_unset=True)
    update = PaymentModel.update_payment(payment_id, update_fields)
    if not update:
        logging.info("Admin ID %s failed updating Payment ID %s",
                     current_user.id, payment_id)
        raise HTTPException(status_code=500,
                            detail="Payment has failed")
    return {"message": "Payment updated successfully"}


@router.get("/payments/refunds")
async def get_refund_requests(user_id: int | None = None,
                              current_user: User = Depends(require_role(
                               UserRole.PAYMENTADMIN, UserRole.SUPERADMIN))):
    """
    Retrieve refund requests for all users or a specific user.

    Args:
        user_id (int | None): Optional ID of the user to filter refund requests.
                              If None, returns refunds for all users.
        current_user (User): The currently authenticated admin user.

    Raises:
        HTTPException: 
            404 if the specified user does not exist.
            404 if no refund requests are found.

    Returns:
        list[dict]: A list of refund request objects.
    """
    if user_id:
        user = user_model.get_user_by_id(user_id)
        if not user:
            logger.warning("Admin ID %s tried getting refunds from"
                           "nonexistent User ID %s",
                           current_user.id, user_id)
            raise HTTPException(status_code=404,
                                detail="User not found")
    refunds = PaymentModel.get_refund_requests(user_id)
    if not refunds:
        logger.warning("Admin ID %s tried getting refunds, "
                       "but none were found", current_user.id)
        raise HTTPException(status_code=404,
                            detail="No refunds found")
    logger.info("Admin ID %s retrieved refunds",
                current_user.id)
    return refunds


@router.post("/payments/{payment_id}/request_refund")
async def request_refund(payment_id: int,
                         current_user: User = Depends(get_current_user)):
    """
    Request a refund for a specific payment.

    Args:
        payment_id (int): The ID of the payment for which to request a refund.
        current_user (User): The currently authenticated user.

    Raises:
        HTTPException:
            404 if the payment does not exist.
            403 if the payment does not belong to the current user.
            400 if the payment has not yet been completed.
            400 if a refund has already been requested.
            500 if marking the refund request fails.

    Returns:
        dict: A success message if the refund request is recorded.
    """
    payment = PaymentModel.get_payment_by_payment_id(payment_id)
    if not payment:
        logger.warning("User ID %s tried requesting a refund for payment %s, "
                       "but it was not found", current_user.id, payment_id)
        raise HTTPException(status_code=404,
                            detail="Payment not found")
    if payment["user_id"] != current_user.id:
        logger.info("User ID %s tried request refund for Payment ID %s, "
                    "but it does not belong to user",
                    current_user.id, payment_id)
        raise HTTPException(status_code=403,
                            detail="This payment does not belong to this user")
    if not payment["completed"]:
        logger.info("User ID %s tried request refund for Payment ID %s, "
                    "but it has not yet been paid",
                    current_user.id, payment_id)
        raise HTTPException(status_code=400,
                            detail="Payment has not yet been paid")
    if payment["refund_requested"]:
        logger.info("User ID %s tried request refund for Payment ID %s, "
                    "but a refund has already been requested",
                    current_user.id, payment_id)
        raise HTTPException(status_code=400,
                            detail="Refund has already been requested")
    update = PaymentModel.mark_refund_request(payment_id)
    if not update:
        logger.info("User ID %s tried request refund for Payment ID %s, "
                    "but something went wrong",
                    current_user.id, payment_id)
        raise HTTPException(status_code=500,
                            detail="Request has failed")
    return {"message": "Refund requested successfully"}


@router.post("/payments/{payment_id}/give_refund")
async def give_refund(
    payment_id: int,
    current_user: User = Depends(get_current_user)
):
    payment = PaymentModel.get_payment_by_payment_id(payment_id)
    if not payment:
        logger.warning("User ID %s tried refunding payment %s, "
                       "but it was not found", current_user.id, payment_id)
        raise HTTPException(status_code=404,
                            detail="Payment not found")
    if not user_can_manage_lot(current_user, payment["parking_lot_id"],
                               for_payments=True):
        raise HTTPException(status_code=403,
                            detail="Not enough permissions for this lot")
    if not payment["completed"]:
        logger.info("User ID %s tried refundnig Payment ID %s, "
                    "but it has not yet been paid",
                    current_user.id, payment_id)
        raise HTTPException(status_code=400,
                            detail="Payment has not yet been paid")
    if payment["refund_accepted"]:
        logger.info("User ID %s tried to refund Payment ID %s, "
                    "but a refund has given",
                    current_user.id, payment_id)
        raise HTTPException(status_code=400,
                            detail="Refund has already been given")
    update = PaymentModel.give_refund(current_user.id, payment_id)
    if not update:
        logger.info("User ID %s tried refunding Payment ID %s, "
                    "but something went wrong",
                    current_user.id, payment_id)
        raise HTTPException(status_code=500,
                            detail="Refund has failed")
    return {"message": "Refund given successfully"}


@router.get("/payments/{payment_id}")
async def get_payment_by_id(payment_id: int,
                            current_user: User = Depends(require_role(
                             UserRole.PAYMENTADMIN, UserRole.SUPERADMIN))):
    """
    Retrieve a specific payment by its ID.

    Args:
        payment_id (int): The ID of the payment to retrieve.
        current_user (User): The currently authenticated admin user.

    Raises:
        HTTPException:
            404 if the payment does not exist.

    Returns:
        dict: The payment data for the specified ID.
    """
    payment = PaymentModel.get_payment_by_payment_id(payment_id)
    if not payment:
        logger.info("Admin ID %s tried to delete nonexistent Payment ID %s",
                    current_user.id, payment_id)
        raise HTTPException(status_code=404,
                            detail="Payment not found")
    if not user_can_manage_lot(current_user, payment["parking_lot_id"],
                               for_payments=True):
        raise HTTPException(status_code=403,
                            detail="Not enough permissions for this lot")
    logger.info("Admin ID %s retrieved Payment ID %s",
                current_user.id, payment_id)
    return payment


@router.delete("/payments/{payment_id}")
async def delete_payment(payment_id: int,
                         current_user: User = Depends(require_role(
                          UserRole.PAYMENTADMIN, UserRole.SUPERADMIN))):
    """
    Delete a specific payment by its ID.

    Args:
        payment_id (int): The ID of the payment to delete.
        current_user (User): The currently authenticated admin user.

    Raises:
        HTTPException:
            404 if the payment does not exist.
            500 if deleting the payment fails.

    Returns:
        dict: A success message if the payment was deleted.
    """
    payment = PaymentModel.get_payment_by_payment_id(payment_id)
    if not payment:
        logger.info("Admin ID %s tried to delete nonexistent Payment ID %s",
                    current_user.id, payment_id)
        raise HTTPException(status_code=404, detail="Payment not found")
    if not user_can_manage_lot(current_user, payment["parking_lot_id"],
                               for_payments=True):
        raise HTTPException(status_code=403,
                            detail="Not enough permissions for this lot")
    delete = PaymentModel.delete_payment(payment_id)
    if not delete:
        logger.info("Admin ID %s tried to delete Payment ID %s, but failed",
                    current_user.id, payment_id)
        raise HTTPException(status_code=500, detail="Deletion has failed")
    logger.info("Admin ID %s deleted Payment ID %s",
                current_user.id, payment_id)
    return {"message": "Payment deleted successfully"}

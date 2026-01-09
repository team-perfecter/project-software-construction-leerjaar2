from api.datatypes.user import User, UserRole
from api.datatypes.discount_code import DiscountCodeCreate
from api.models.discount_code_model import DiscountCodeModel
from fastapi import Depends, APIRouter, HTTPException
from api.auth_utils import require_role
from datetime import date

import logging
logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["discount_codes"]
)

discount_code_model: DiscountCodeModel = DiscountCodeModel()

retrieved_succesfully_message = "Discount codes retrieved successfully"

@router.post("/discount-codes")
async def create_discount_code(d: DiscountCodeCreate,
                         current_user: User = Depends(require_role(UserRole.SUPERADMIN))):
    current_codes = discount_code_model.get_all_active_discount_codes()
    for discount_code in current_codes:
        if d.code == discount_code["code"]:
            logger.error("Admin ID %i tried to create discount code %i, "
                         "but it already exists",
                         current_user.id, d.code)
            raise HTTPException(status_code=409,
                                detail="Discount code already exists")
    if d.discount_type != "percentage" and d.discount_type != "fixed":
        logger.error("Admin ID %i tried to create a discount code, but entered invalid discount type %i",
                     current_user.id, d.discount_type)
        raise HTTPException(status_code=400,
                            detail="Discount type must be percentage or fixed")
    if d.discount_value <= 0:
        logger.error("Admin ID %i tried to create discount code with discount value %i",
                     current_user.id, d.discount_value)
        raise HTTPException(status_code=400,
                            detail="Discount value must be a postive number")
    if d.minimum_price is not None and d.minimum_price <= 0:
            logger.error("Admin ID %i tried to create discount code with minimum price %i",
                         current_user.id, d.use_amount)
            raise HTTPException(status_code=400,
                            detail="Minimum price must be a postive number")
    if d.use_amount is not None and d.use_amount <= 0:
            logger.error("Admin ID %i tried to create discount code with use amount %i",
                         current_user.id, d.use_amount)
            raise HTTPException(status_code=400,
                            detail="Use amount must be a postive number")
    if (d.start_applicable_time is None) != (d.end_applicable_time is None):
        logger.error("Admin ID %i tried to create discount code with only one applicable time set", current_user.id)
        raise HTTPException(
            status_code=400,
            detail="Both start_applicable_time and end_applicable_time must be set together")
    if d.start_applicable_time and d.end_applicable_time:
        if d.start_applicable_time >= d.end_applicable_time:
            logger.error("Admin ID %i tried to create discount code with start_applicable_time >= end_applicable_time", current_user.id)
            raise HTTPException(
                status_code=400,
                detail="start_applicable_time must be before end_applicable_time")
    if d.end_date is not None and d.end_date <= date.today():
        logger.error("Admin ID %i tried to create discount code with end_date in the past", current_user.id)
        raise HTTPException(status_code=400,
                            detail="End date must be in the future")
    created = discount_code_model.create_discount_code(d)
    if not created:
        logger.error("Admin ID %i tried to create a discount code, but failed",
                     current_user.id)
        raise HTTPException(status_code=500,
                            detail="Failed to create discount code")
    logger.info("Admin ID %i created new discount code",
                 current_user.id)
    locations = discount_code_model.get_all_locations_by_code(d.code)
    created["locations"] = locations
    return {
        "message": "Discount codes created successfully",
        "discount_code": created}


@router.get("/discount-codes")
async def get_all_discount_codes(current_user: User = Depends(require_role(UserRole.SUPERADMIN))):
    results = discount_code_model.get_all_discount_codes()
    if not results:
        logger.error("Admin ID %s tried to get all discount codes but there were none",
                     current_user.id)
        raise HTTPException(status_code=404,
                            detail="No discount codes were found.")
    logger.info("Admin ID %i retrieved all discount codes",
                current_user.id)
    for discount_code in results:
        locations = discount_code_model.get_all_locations_by_code(discount_code["code"])
        discount_code["locations"] = locations
    return {
        "message": retrieved_succesfully_message,
        "discount_code": results}

@router.get("/discount-codes/active")
async def get_all_discount_codes(current_user: User = Depends(require_role(UserRole.SUPERADMIN))):
    results = discount_code_model.get_all_active_discount_codes()
    if not results:
        logger.error("Admin ID %s tried to get all active discount codes but there were none",
                     current_user.id)
        raise HTTPException(status_code=404,
                            detail="No active discount codes were found.")
    logger.info("Admin ID %i retrieved all active discount codes",
                current_user.id)
    for discount_code in results:
        locations = discount_code_model.get_all_locations_by_code(discount_code["code"])
        discount_code["locations"] = locations
    return {
        "message": retrieved_succesfully_message,
        "discount_code": results}


@router.get("/discount-codes/{code}")
async def get_discord_code_by_code(code: str, current_user: User = Depends(require_role(UserRole.SUPERADMIN))):
    discount_code = discount_code_model.get_discount_code_by_code(code)
    if not discount_code:
        logger.error("Admin ID %s tried to get discount code %i, "
                     "but it was not found",
                     current_user.id, code)
        raise HTTPException(status_code=404,
                            detail="No discount code was found.")
    logger.info("Admin ID %i retrieved data for discount code %i",
                current_user.id, code)
    locations = discount_code_model.get_all_locations_by_code(code)
    discount_code["locations"] = locations
    return {
        "message": retrieved_succesfully_message,
        "discount_code": discount_code}


@router.post("/discount-codes/{code}/deactivate")
async def deactive_discount_code(code: str, current_user: User = Depends(require_role(UserRole.SUPERADMIN))):
    discount_code = discount_code_model.get_discount_code_by_code(code)
    if not discount_code:
        logger.error("Admin ID %i tried to get discount code %i, but no result",
                     current_user.id, code)
        raise HTTPException(status_code=404,
                            detail="Discount code not found")
    if discount_code["active"] is not True:
        logger.error("Admin ID %i tried to deactive discount code %i, "
                     "but it was not active",
                     current_user.id, code)
        raise HTTPException(status_code=400,
                            detail="Discount code was not active")
    deactivated = discount_code_model.deactive_discount_code(code)
    if not deactivated:
        logger.error("Admin ID %i tried to deactive discount code %i, "
                     "but something went wrong",
                     current_user.id, code)
        raise HTTPException(status_code=500,
                            detail="Update was unsuccesful")
    logger.info("Admin ID %i deactived discount code %i",
                current_user.id, code)
    locations = discount_code_model.get_all_locations_by_code(code)
    discount_code["locations"] = locations
    return {
        "message": "Discount code deactivated successfully",
        "discount_code": deactivated}

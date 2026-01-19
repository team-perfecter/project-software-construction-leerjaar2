import logging
from fastapi import Depends, APIRouter, HTTPException
from api.datatypes.user import User, UserRole
from api.datatypes.discount_code import DiscountCodeCreate, DiscountCodeUpdate
from api.models.discount_code_model import DiscountCodeModel
from api.auth_utils import require_role
from api.utilities.discount_code_validation import (
    create_or_update_discount_code_validation
)
from psycopg2.errors import UniqueViolation
logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["discount_codes"]
)

discount_code_model: DiscountCodeModel = DiscountCodeModel()

retrieved_succesfully_message = "Discount codes retrieved successfully"


@router.post("/discount-codes", status_code=201)
async def create_discount_code(d: DiscountCodeCreate,
                               current_user: User = Depends(
                                   require_role(UserRole.SUPERADMIN))):
    create_or_update_discount_code_validation(d, current_user)
    try:
        created = discount_code_model.create_discount_code(d)
    except UniqueViolation:
        logger.error("Admin ID %s tried to create duplicate discount code %s",
                     current_user.id, d.code)
        raise HTTPException(status_code=409,
                            detail="Discount code already exists")
    if not created:
        logger.error("Admin ID %s tried to create a discount code, but failed",
                     current_user.id)
        raise HTTPException(status_code=500,
                            detail="Failed to create discount code")
    logger.info("Admin ID %s created new discount code",
                current_user.id)
    locations = discount_code_model.get_all_locations_by_code(d.code)
    created["locations"] = locations
    return {
        "message": "Discount codes created successfully",
        "discount_code": created}


@router.get("/discount-codes")
async def get_all_discount_codes(
    current_user: User = Depends(
        require_role(UserRole.SUPERADMIN))):
    results = discount_code_model.get_all_discount_codes()
    if not results:
        logger.error("Admin ID %s tried to get all discount codes, "
                     "but there were none",
                     current_user.id)
        raise HTTPException(status_code=404,
                            detail="No discount codes were found.")
    logger.info("Admin ID %s retrieved all discount codes",
                current_user.id)
    for discount_code in results:
        locations = discount_code_model.get_all_locations_by_code(
            discount_code["code"])
        discount_code["locations"] = locations
    return {
        "message": retrieved_succesfully_message,
        "discount_code": results}


@router.get("/discount-codes/active")
async def get_all_active_discount_codes(
    current_user: User = Depends(
        require_role(UserRole.SUPERADMIN))):
    results = discount_code_model.get_all_active_discount_codes()
    if not results:
        logger.error("Admin ID %s tried to get all active discount codes, "
                     "but there were none",
                     current_user.id)
        raise HTTPException(status_code=404,
                            detail="No active discount codes were found.")
    logger.info("Admin ID %s retrieved all active discount codes",
                current_user.id)
    for discount_code in results:
        locations = discount_code_model.get_all_locations_by_code(
            discount_code["code"])
        discount_code["locations"] = locations
    return {
        "message": retrieved_succesfully_message,
        "discount_code": results}


@router.get("/discount-codes/{code}")
async def get_discord_code_by_code(
    code: str,
    current_user: User = Depends(
        require_role(UserRole.SUPERADMIN))):
    discount_code = discount_code_model.get_discount_code_by_code(code)
    if not discount_code:
        logger.error("Admin ID %s tried to get discount code %s, "
                     "but it was not found",
                     current_user.id, code)
        raise HTTPException(status_code=404,
                            detail="No discount code was found.")
    logger.info("Admin ID %s retrieved data for discount code %s",
                current_user.id, code)
    locations = discount_code_model.get_all_locations_by_code(code)
    discount_code["locations"] = locations
    return {
        "message": retrieved_succesfully_message,
        "discount_code": discount_code}


@router.post("/discount-codes/{code}/deactivate")
async def deactive_discount_code(
    code: str, current_user: User = Depends(
        require_role(UserRole.SUPERADMIN))):
    discount_code = discount_code_model.get_discount_code_by_code(code)
    if not discount_code:
        logger.error("Admin ID %s tried to get discount code %s, "
                     "but no result",
                     current_user.id, code)
        raise HTTPException(status_code=404,
                            detail="Discount code not found")
    if discount_code["active"] is not True:
        logger.error("Admin ID %s tried to deactive discount code %s, "
                     "but it was not active",
                     current_user.id, code)
        raise HTTPException(status_code=400,
                            detail="Discount code was not active")
    deactivated = discount_code_model.deactivate_discount_code(code)
    if not deactivated:
        logger.error("Admin ID %s tried to deactive discount code %s, "
                     "but something went wrong",
                     current_user.id, code)
        raise HTTPException(status_code=500,
                            detail="Update was unsuccesful")
    logger.info("Admin ID %s deactived discount code %s",
                current_user.id, code)
    locations = discount_code_model.get_all_locations_by_code(code)
    discount_code["locations"] = locations
    return {
        "message": "Discount code deactivated successfully",
        "discount_code": deactivated}


@router.delete("/discount-codes/{code}")
async def delete_discount_code(
    code: str,
    current_user: User = Depends(
        require_role(UserRole.SUPERADMIN))):
    discount_code = discount_code_model.get_discount_code_by_code(code)
    if not discount_code:
        logging.info("Admin ID %s tried to delete "
                     "nonexistent discount code %s",
                     current_user.id, code)
        raise HTTPException(status_code=404, detail="Discount code not found")
    delete = discount_code_model.delete_discount_code(code)
    if not delete:
        logging.info("Admin ID %s tried to delete discount code %s,"
                     "but failed",
                     current_user.id, code)
        raise HTTPException(status_code=500, detail="Deletion has failed")
    logging.info("Admin ID %s deleted discount code ID %s",
                 current_user.id, code)
    return {"message": "Siscount code deleted successfully",
            "discount_code": code}


@router.put("/discount-codes/{code}")
async def update_discount_code(
    code: str,
    d: DiscountCodeUpdate,
    current_user: User = Depends(
        require_role(UserRole.SUPERADMIN)
    ),
):
    discount_code = discount_code_model.get_discount_code_by_code(code)
    if not discount_code:
        logging.info("Admin ID %s tried updating discount code %s, "
                     "but it does not exist", current_user.id, code)
        raise HTTPException(status_code=404,
                            detail="Discount code not found")
    create_or_update_discount_code_validation(d, current_user)
    update_fields = d.dict(exclude_unset=True)
    try:
        update = discount_code_model.update_discount_code(code, update_fields)
    except UniqueViolation:
        logger.error("Admin ID %s tried to create duplicate discount code %s",
                     current_user.id, d.code)
        raise HTTPException(status_code=409,
                            detail="Discount code already exists")
    if not update:
        logging.info("Admin ID %s failed updating discount code %s",
                     current_user.id, code)
        raise HTTPException(status_code=500,
                            detail="Update has has failed")
    locations = discount_code_model.get_all_locations_by_code(d.code)
    update["locations"] = locations
    return {"message": "Discount code updated successfully",
            "discount_code": update}

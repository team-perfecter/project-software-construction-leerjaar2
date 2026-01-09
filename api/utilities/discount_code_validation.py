from api.models.discount_code_model import DiscountCodeModel
from api.datatypes.reservation import ReservationCreate
from api.datatypes.parking_lot import Parking_lot
from api.datatypes.user import User
from api.datatypes.discount_code import DiscountCodeCreate
from fastapi import HTTPException
from datetime import datetime, date
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)
discount_code_model: DiscountCodeModel=DiscountCodeModel()

def use_discount_code_validation(discount_code: Dict[str, Any], reservation: ReservationCreate, current_user: User, parking_lot: Parking_lot):
    if discount_code["user_id"] is not None and current_user.id != discount_code["user_id"]:
        logger.error("User ID %s tried to use discount code %s, "
                    "but doesn't have permission",
                    current_user.id, reservation.discount_code)
        raise HTTPException(status_code=400,
                            detail="This account can not use this discount code")
    
    locations = discount_code_model.get_all_locations_by_code(discount_code["code"])
    if locations and parking_lot.location not in locations:
        logger.error(
        "User ID %s tried to use discount code %s, but it is not applicable in location %s",
        current_user.id, discount_code["code"], parking_lot.location)
        raise HTTPException(
            status_code=400,
            detail="This discount code is not valid for this parking lot location")
    if discount_code["start_applicable_time"] is not None and discount_code["end_applicable_time"] is not None:
        now = datetime.now().time()
        if not (discount_code["start_applicable_time"] <= now <= discount_code["end_applicable_time"]):
            logger.error(
                "User ID %s tried to use discount code %s, but current time %s is not between %s and %s",
                current_user.id,
                discount_code["code"],
                now,
                discount_code["start_applicable_time"],
                discount_code["end_applicable_time"])
            raise HTTPException(
                status_code=400,
                detail="This discount code is not valid at this time")
    if discount_code["use_amount"] >= discount_code["used_count"]:
        logger.error("User ID %s tried to use discount code %s, "
                    "but it has reached it max use count %s",
                    current_user.id, reservation.discount_code, discount_code["use_amount"])
        raise HTTPException(status_code=400,
                            detail="This discount code has reached it's max uses")
    if datetime.now() >= datetime.fromisoformat(discount_code["end_date"]):
        logger.error("User ID %s tried to use discount code %s, "
                    "but it has reached past it's end date %s",
                    current_user.id, reservation.discount_code, discount_code["end_date"])
        raise HTTPException(status_code=400,
                            detail="This discount code has expired")
    if discount_code["active"] is False:
        logger.error("User ID %s tried to use discount code %s, "
                    "but it it inactive",
                    current_user.id, reservation.discount_code)
        raise HTTPException(status_code=400,
                            detail="This discount code has expired")
    incremented = discount_code_model.increment_used_count(discount_code["id"])
    if not incremented:
        logger.error("Incrementing discount code's used count %s has failed",
                    reservation.discount_code)
        raise HTTPException(status_code=500,
                            detail="Failed to increment discount code's use count")


def create_or_update_discount_code_validation(d: DiscountCodeCreate, current_user: User):
    if d.discount_type is not None and d.discount_type != "percentage" and d.discount_type != "fixed":
        logger.error("Admin ID %s tried to create a discount code, but entered invalid discount type %s",
                     current_user.id, d.discount_type)
        raise HTTPException(status_code=400,
                            detail="Discount type must be percentage or fixed")
    if d.discount_value is not None and d.discount_value <= 0:
        logger.error("Admin ID %s tried to create discount code with discount value %s",
                     current_user.id, d.discount_value)
        raise HTTPException(status_code=400,
                            detail="Discount value must be a postive number")
    if d.minimum_price is not None and d.minimum_price <= 0:
            logger.error("Admin ID %s tried to create discount code with minimum price %s",
                         current_user.id, d.use_amount)
            raise HTTPException(status_code=400,
                            detail="Minimum price must be a postive number")
    if d.use_amount is not None and d.use_amount <= 0:
            logger.error("Admin ID %s tried to create discount code with use amount %s",
                         current_user.id, d.use_amount)
            raise HTTPException(status_code=400,
                            detail="Use amount must be a postive number")
    if (d.start_applicable_time is None) != (d.end_applicable_time is None):
        logger.error("Admin ID %s tried to create discount code with only one applicable time set", current_user.id)
        raise HTTPException(
            status_code=400,
            detail="Both start_applicable_time and end_applicable_time must be set together")
    if d.start_applicable_time is not None and d.end_applicable_time is not None:
        if d.start_applicable_time >= d.end_applicable_time:
            logger.error("Admin ID %s tried to create discount code with start_applicable_time >= end_applicable_time", current_user.id)
            raise HTTPException(
                status_code=400,
                detail="start_applicable_time must be before end_applicable_time")
    if d.end_date is not None and d.end_date <= date.today():
        logger.error("Admin ID %s tried to create discount code with end_date in the past", current_user.id)
        raise HTTPException(status_code=400,
                            detail="End date must be in the future")
    if d.start_date is not None and d.end_date is not None and d.start_date >= d.end_date:
        logger.error("Admin ID %s tried to create discount code with start_date >= end_date", current_user.id)
        raise HTTPException(
            status_code=400,
            detail="start_date must be before end_date")
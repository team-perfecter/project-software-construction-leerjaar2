from api.models.discount_code_model import DiscountCodeModel
from api.datatypes.reservation import ReservationCreate
from api.datatypes.user import User
from api.datatypes.parking_lot import Parking_lot
from fastapi import HTTPException
from datetime import datetime
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)
discount_code_model: DiscountCodeModel=DiscountCodeModel()

def discount_code_validation(discount_code: Dict[str, Any], reservation: ReservationCreate, current_user: User, parking_lot: Parking_lot):
    if discount_code["user_id"] is not None and current_user.id != discount_code["user_id"]:
        logger.error("User ID %s tried to use discount code %i, "
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
        logger.error("User ID %s tried to use discount code %i, "
                    "but it has reached it max use count %i",
                    current_user.id, reservation.discount_code, discount_code["use_amount"])
        raise HTTPException(status_code=400,
                            detail="This discount code has reached it's max uses")
    if datetime.now() >= datetime.fromisoformat(discount_code["end_date"]):
        logger.error("User ID %s tried to use discount code %i, "
                    "but it has reached past it's end date %i",
                    current_user.id, reservation.discount_code, discount_code["end_date"])
        raise HTTPException(status_code=400,
                            detail="This discount code has expired")
    if discount_code["active"] is False:
        logger.error("User ID %s tried to use discount code %i, "
                    "but it it inactive",
                    current_user.id, reservation.discount_code)
        raise HTTPException(status_code=400,
                            detail="This discount code has expired")
    incremented = discount_code_model.increment_used_count(discount_code["id"])
    if not incremented:
        logger.error("Incrementing discount code's used count %i has failed",
                    reservation.discount_code)
        raise HTTPException(status_code=500,
                            detail="Failed to increment discount code's use count")
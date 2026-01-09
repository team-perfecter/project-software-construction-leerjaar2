from datetime import date
from pydantic import BaseModel
from typing import Optional, List


class DiscountCodeCreate(BaseModel):
    code: str
    user_id: Optional[int] = None
    discount_type: str
    discount_value: float
    use_amount: Optional[int] = None
    minimum_price: Optional[float] = None
    end_date: Optional[date] = None
    locations: Optional[List[str]] = []


class DiscountCode(DiscountCodeCreate):
    used_count: int
    active: bool

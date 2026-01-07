from datetime import date
from pydantic import BaseModel
from typing import Optional


class DiscountCodeCreate(BaseModel):
    code: str
    discount_type: str
    discount_value: int
    use_amount: Optional[int] = None
    end_date: Optional[date] = None


class DiscountCode(DiscountCodeCreate):
    id: int
    used_count: int
    active: bool

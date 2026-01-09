from datetime import date, time
from pydantic import BaseModel
from typing import Optional, List


class DiscountCodeCreate(BaseModel):
    code: str
    user_id: Optional[int] = None
    discount_type: str
    discount_value: float
    use_amount: Optional[int] = None
    minimum_price: Optional[float] = None
    start_applicable_time: Optional[time] = None
    end_applicable_time: Optional[time] = None
    end_date: Optional[date] = None
    locations: Optional[List[str]] = []


class DiscountCode(DiscountCodeCreate):
    used_count: int
    active: bool


class DiscountCodeUpdate(BaseModel):
    code: Optional[str] = None
    user_id: Optional[int] = None
    discount_type: Optional[str] = None
    discount_value: Optional[int] = None
    use_amount: Optional[int] = None
    minimum_price: Optional[float] = None
    start_applicable_time: Optional[time] = None
    end_applicable_time: Optional[time] = None
    end_date: Optional[date] = None
    used_count: Optional[int] = None
    active: Optional[bool] = None


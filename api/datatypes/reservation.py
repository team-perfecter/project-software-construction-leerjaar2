from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class ReservationCreate(BaseModel):
    user_id: int
    vehicle_id: int
    parking_lot_id: int
    start_time: datetime
    end_time: datetime | None
    discount_code: Optional[str] = None


class Reservation(ReservationCreate):
    id: int
    created_at: datetime
    cost: int
    status: str

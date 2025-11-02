from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class Session(BaseModel):
    id: int
    parking_lot_id: int
    payment_id: Optional[int] = None
    user_id: int
    vehicle_id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_in_minutes: Optional[int] = None
    cost: Optional[float] = None
    payment_status: str = "pending"

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SessionCreate(BaseModel):
    parking_lot_id: int
    user_id: int
    vehicle_id: int
    reservation_id: Optional[int] = None


class Session(SessionCreate):
    id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    cost: Optional[float] = None
